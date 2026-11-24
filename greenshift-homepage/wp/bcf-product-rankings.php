<?php
/**
 * Plugin Name: BCF Product Rankings
 * Description: Scores products for the homepage "Most popular" and "New products" loops, and stores each product's brand name and brand page link for the product cards.
 * Version:     1.0.0
 *
 * Install as a must-use plugin: copy this file to wp-content/mu-plugins/.
 *
 * Writes four product meta keys that the GreenShift query loops and cards read:
 *   _bcf_popular_score  Number of separate orders containing the product in the last POPULAR_DAYS.
 *   _bcf_new_score      Launch score for recent products (orders since launch, price, recency, Featured).
 *   _bcf_brand          Brand name, from the brand attribute.
 *   _bcf_brand_url      Link to the product category with the same name as the brand.
 *
 * Scores refresh twice a day, or on demand from WooCommerce > Product rankings.
 */

defined( 'ABSPATH' ) || exit;

final class BCF_Product_Rankings {

	/** Settings. Change these to tune the rankings. */
	const BRAND_ATTRIBUTE    = 'pa_brand';                // Global attribute taxonomy holding the brand.
	const POPULAR_DAYS       = 90;                        // Look-back window for "Most popular".
	const NEW_DAYS           = 120;                       // Products published within this many days count as new.
	const NEW_MIN_CANDIDATES = 40;                        // Always score at least this many of the newest products.
	const NEW_HALF_LIFE_DAYS = 30;                        // A new product's score halves every this many days.
	const FEATURED_BOOST     = 3.0;                       // Multiplier for products starred as Featured.
	const EXCLUDE_TAG        = 'exclude-from-rankings';   // Product tag slug that keeps a product out of both rankings.
	const ORDER_STATUSES     = array( 'wc-completed', 'wc-processing' );

	const META_POPULAR = '_bcf_popular_score';
	const META_NEW     = '_bcf_new_score';
	const META_BRAND   = '_bcf_brand';
	const META_BRANDURL = '_bcf_brand_url';
	const CRON_HOOK    = 'bcf_rankings_refresh';
	const OPTION_LAST  = 'bcf_rankings_last_run';

	public static function init() {
		add_action( 'init', array( __CLASS__, 'schedule' ) );
		add_action( self::CRON_HOOK, array( __CLASS__, 'refresh' ) );
		add_action( 'woocommerce_update_product', array( __CLASS__, 'sync_brand' ) );
		add_action( 'woocommerce_new_product', array( __CLASS__, 'sync_brand' ) );
		add_action( 'admin_menu', array( __CLASS__, 'admin_menu' ) );
		add_action( 'admin_post_bcf_rankings_refresh', array( __CLASS__, 'handle_refresh' ) );
		if ( defined( 'WP_CLI' ) && WP_CLI ) {
			WP_CLI::add_command( 'bcf rankings', array( __CLASS__, 'cli' ) );
		}
	}

	public static function schedule() {
		if ( ! wp_next_scheduled( self::CRON_HOOK ) ) {
			wp_schedule_event( time() + 60, 'twicedaily', self::CRON_HOOK );
		}
	}

	/* ------------------------------------------------------------------ */
	/* Scoring (pure functions, unit tested in wp/test-rankings.php)        */
	/* ------------------------------------------------------------------ */

	/**
	 * How much weight a product's price gives a launch. Logarithmic, so a $559 tool
	 * counts about 2.3x a $5 bit, not 100x.
	 */
	public static function price_weight( $price ) {
		return log10( max( 0.0, (float) $price ) + 10.0 );
	}

	/** Halves every NEW_HALF_LIFE_DAYS. */
	public static function recency_weight( $age_days ) {
		return pow( 0.5, max( 0.0, (float) $age_days ) / self::NEW_HALF_LIFE_DAYS );
	}

	/**
	 * Launch score for a new product. One order since launch is worth a lot early on,
	 * and every product starts at 1 so price and recency still sort products with no orders yet.
	 */
	public static function new_score( $orders_since_launch, $price, $age_days, $featured ) {
		$score = ( 1 + max( 0, (int) $orders_since_launch ) )
			* self::price_weight( $price )
			* self::recency_weight( $age_days )
			* ( $featured ? self::FEATURED_BOOST : 1.0 );
		return round( $score, 4 );
	}

	/* ------------------------------------------------------------------ */
	/* Refresh                                                              */
	/* ------------------------------------------------------------------ */

	public static function refresh() {
		if ( ! function_exists( 'wc_get_product' ) ) {
			return array();
		}
		$excluded = self::excluded_ids();
		$popular  = self::popular_counts( $excluded );
		$new      = self::new_scores( $excluded );

		self::write_scores( self::META_POPULAR, $popular );
		self::write_scores( self::META_NEW, $new );
		$brands = self::sync_all_brands();

		$summary = array(
			'popular' => count( $popular ),
			'new'     => count( $new ),
			'brands'  => $brands,
			'time'    => current_time( 'mysql' ),
		);
		update_option( self::OPTION_LAST, $summary, false );
		return $summary;
	}

	/** Separate orders per product in the window. Variations count toward their parent. */
	private static function popular_counts( array $excluded ) {
		global $wpdb;
		$since    = gmdate( 'Y-m-d H:i:s', current_time( 'timestamp' ) - self::POPULAR_DAYS * DAY_IN_SECONDS );
		$statuses = "'" . implode( "','", array_map( 'esc_sql', self::ORDER_STATUSES ) ) . "'";
		$rows     = $wpdb->get_results(
			$wpdb->prepare(
				"SELECT l.product_id, COUNT(DISTINCT l.order_id) AS orders
				FROM {$wpdb->prefix}wc_order_product_lookup l
				INNER JOIN {$wpdb->prefix}wc_order_stats s ON s.order_id = l.order_id
				WHERE s.status IN ($statuses) AND s.parent_id = 0 AND l.date_created >= %s
				GROUP BY l.product_id",
				$since
			)
		);
		$out = array();
		foreach ( $rows as $row ) {
			$id = (int) $row->product_id;
			if ( $id && ! isset( $excluded[ $id ] ) ) {
				$out[ $id ] = (int) $row->orders;
			}
		}
		return $out;
	}

	private static function new_scores( array $excluded ) {
		global $wpdb;
		$now      = current_time( 'timestamp' );
		$cutoff   = gmdate( 'Y-m-d H:i:s', $now - self::NEW_DAYS * DAY_IN_SECONDS );
		$recent   = get_posts(
			array(
				'post_type'      => 'product',
				'post_status'    => 'publish',
				'fields'         => 'ids',
				'posts_per_page' => -1,
				'date_query'     => array( array( 'after' => $cutoff, 'inclusive' => true ) ),
				'no_found_rows'  => true,
			)
		);
		$newest   = get_posts(
			array(
				'post_type'      => 'product',
				'post_status'    => 'publish',
				'fields'         => 'ids',
				'posts_per_page' => self::NEW_MIN_CANDIDATES,
				'orderby'        => 'date',
				'order'          => 'DESC',
				'no_found_rows'  => true,
			)
		);
		$ids = array_diff( array_unique( array_map( 'intval', array_merge( $recent, $newest ) ) ), array_keys( $excluded ) );
		if ( ! $ids ) {
			return array();
		}

		$statuses = "'" . implode( "','", array_map( 'esc_sql', self::ORDER_STATUSES ) ) . "'";
		$in       = implode( ',', array_map( 'intval', $ids ) );
		$rows     = $wpdb->get_results(
			"SELECT l.product_id, COUNT(DISTINCT l.order_id) AS orders
			FROM {$wpdb->prefix}wc_order_product_lookup l
			INNER JOIN {$wpdb->prefix}wc_order_stats s ON s.order_id = l.order_id
			INNER JOIN {$wpdb->posts} p ON p.ID = l.product_id
			WHERE l.product_id IN ($in) AND s.status IN ($statuses) AND s.parent_id = 0 AND l.date_created >= p.post_date
			GROUP BY l.product_id"
		);
		$orders = array();
		foreach ( $rows as $row ) {
			$orders[ (int) $row->product_id ] = (int) $row->orders;
		}

		$featured = array_flip( array_map( 'intval', wc_get_featured_product_ids() ) );
		$out      = array();
		foreach ( $ids as $id ) {
			$product = wc_get_product( $id );
			if ( ! $product ) {
				continue;
			}
			$age        = ( $now - get_post_time( 'U', false, $id ) ) / DAY_IN_SECONDS;
			$out[ $id ] = self::new_score( $orders[ $id ] ?? 0, $product->get_price(), $age, isset( $featured[ $id ] ) );
		}
		return $out;
	}

	private static function excluded_ids() {
		$ids = get_posts(
			array(
				'post_type'      => 'product',
				'post_status'    => 'any',
				'fields'         => 'ids',
				'posts_per_page' => -1,
				'no_found_rows'  => true,
				'tax_query'      => array(
					array(
						'taxonomy' => 'product_tag',
						'field'    => 'slug',
						'terms'    => self::EXCLUDE_TAG,
					),
				),
			)
		);
		return array_flip( array_map( 'intval', $ids ) );
	}

	/** Writes new scores first, then removes the key from products that no longer qualify, so loops never go empty mid-refresh. */
	private static function write_scores( $key, array $scores ) {
		global $wpdb;
		foreach ( $scores as $id => $score ) {
			update_post_meta( $id, $key, $score );
		}
		$stale = $wpdb->get_col( $wpdb->prepare( "SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key = %s", $key ) );
		foreach ( $stale as $id ) {
			if ( ! isset( $scores[ (int) $id ] ) ) {
				delete_post_meta( (int) $id, $key );
			}
		}
	}

	/* ------------------------------------------------------------------ */
	/* Brand                                                                */
	/* ------------------------------------------------------------------ */

	public static function sync_brand( $product_id ) {
		$product_id = (int) $product_id;
		$terms      = taxonomy_exists( self::BRAND_ATTRIBUTE ) ? wc_get_product_terms( $product_id, self::BRAND_ATTRIBUTE, array( 'fields' => 'all' ) ) : array();
		if ( ! $terms ) {
			delete_post_meta( $product_id, self::META_BRAND );
			delete_post_meta( $product_id, self::META_BRANDURL );
			return;
		}
		$name = $terms[0]->name;
		update_post_meta( $product_id, self::META_BRAND, $name );
		update_post_meta( $product_id, self::META_BRANDURL, self::brand_url( $terms[0] ) );
	}

	/** Brand category page if one matches by slug or name, otherwise a store search for the brand. */
	private static function brand_url( $brand_term ) {
		$cat = get_term_by( 'slug', $brand_term->slug, 'product_cat' );
		if ( ! $cat ) {
			$cat = get_term_by( 'name', $brand_term->name, 'product_cat' );
		}
		if ( $cat && ! is_wp_error( $cat ) ) {
			$link = get_term_link( $cat );
			if ( ! is_wp_error( $link ) ) {
				return $link;
			}
		}
		return add_query_arg( array( 's' => $brand_term->name, 'post_type' => 'product' ), home_url( '/' ) );
	}

	private static function sync_all_brands() {
		$page  = 1;
		$count = 0;
		do {
			$ids = get_posts(
				array(
					'post_type'      => 'product',
					'post_status'    => 'publish',
					'fields'         => 'ids',
					'posts_per_page' => 500,
					'paged'          => $page,
					'no_found_rows'  => true,
				)
			);
			foreach ( $ids as $id ) {
				self::sync_brand( $id );
				$count++;
			}
			$page++;
		} while ( count( $ids ) === 500 );
		return $count;
	}

	/* ------------------------------------------------------------------ */
	/* Admin: WooCommerce > Product rankings                                */
	/* ------------------------------------------------------------------ */

	public static function admin_menu() {
		add_submenu_page( 'woocommerce', 'Product rankings', 'Product rankings', 'manage_woocommerce', 'bcf-rankings', array( __CLASS__, 'admin_page' ) );
	}

	public static function handle_refresh() {
		if ( ! current_user_can( 'manage_woocommerce' ) ) {
			wp_die( 'Not allowed.' );
		}
		check_admin_referer( 'bcf_rankings_refresh' );
		self::refresh();
		wp_safe_redirect( admin_url( 'admin.php?page=bcf-rankings&refreshed=1' ) );
		exit;
	}

	private static function top( $key, $limit ) {
		return get_posts(
			array(
				'post_type'      => 'product',
				'post_status'    => 'publish',
				'posts_per_page' => $limit,
				'meta_key'       => $key,
				'orderby'        => 'meta_value_num',
				'order'          => 'DESC',
				'no_found_rows'  => true,
			)
		);
	}

	public static function admin_page() {
		$last = get_option( self::OPTION_LAST );
		echo '<div class="wrap"><h1>Product rankings</h1>';
		if ( isset( $_GET['refreshed'] ) ) {
			echo '<div class="notice notice-success"><p>Rankings recalculated.</p></div>';
		}
		echo '<p>Last run: ' . esc_html( $last ? $last['time'] : 'never' ) . '. Refreshes twice a day. Tag a product <code>' . esc_html( self::EXCLUDE_TAG ) . '</code> to keep it out of both lists. Star a product as Featured to boost it in New products.</p>';
		echo '<form method="post" action="' . esc_url( admin_url( 'admin-post.php' ) ) . '"><input type="hidden" name="action" value="bcf_rankings_refresh">';
		wp_nonce_field( 'bcf_rankings_refresh' );
		submit_button( 'Recalculate now', 'primary', 'submit', false );
		echo '</form>';
		foreach ( array( self::META_POPULAR => array( 'Most popular (orders in last ' . self::POPULAR_DAYS . ' days)', 7 ), self::META_NEW => array( 'New products (launch score)', 14 ) ) as $key => $info ) {
			echo '<h2>' . esc_html( $info[0] ) . '</h2><table class="widefat striped" style="max-width:760px"><thead><tr><th>#</th><th>Product</th><th>Brand</th><th>Score</th></tr></thead><tbody>';
			foreach ( self::top( $key, $info[1] ) as $i => $post ) {
				printf(
					'<tr><td>%d</td><td><a href="%s">%s</a></td><td>%s</td><td>%s</td></tr>',
					$i + 1,
					esc_url( get_edit_post_link( $post->ID ) ),
					esc_html( get_the_title( $post ) ),
					esc_html( get_post_meta( $post->ID, self::META_BRAND, true ) ),
					esc_html( get_post_meta( $post->ID, $key, true ) )
				);
			}
			echo '</tbody></table>';
		}
		echo '</div>';
	}

	/** wp bcf rankings */
	public static function cli() {
		$summary = self::refresh();
		WP_CLI::success( sprintf( 'Scored %d popular and %d new products, synced %d brands.', $summary['popular'], $summary['new'], $summary['brands'] ) );
	}
}

BCF_Product_Rankings::init();
