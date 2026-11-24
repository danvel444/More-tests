<?php
/**
 * Unit tests for the pure scoring functions in bcf-product-rankings.php.
 * Run: php greenshift-homepage/wp/test-rankings.php
 */
define( 'ABSPATH', __DIR__ );
function add_action() {}
require __DIR__ . '/bcf-product-rankings.php';

$R      = 'BCF_Product_Rankings';
$failed = 0;
function check( $label, $ok ) {
	global $failed;
	echo ( $ok ? 'PASS ' : 'FAIL ' ) . $label . PHP_EOL;
	$failed += $ok ? 0 : 1;
}

$tool_new  = $R::new_score( 0, 559, 3, false );   // New power tool, 3 days old, no orders yet.
$bit_new   = $R::new_score( 0, 4.99, 3, false );  // New driver bit, same age, no orders.
$bit_hot   = $R::new_score( 40, 4.99, 20, false ); // New bit that 40 separate orders picked up.
$tool_old  = $R::new_score( 0, 559, 110, false ); // Same tool, nearly out of the new window.
$feat_bit  = $R::new_score( 0, 4.99, 3, true );   // Bit starred as Featured.

printf( "tool_new=%.3f bit_new=%.3f bit_hot=%.3f tool_old=%.3f feat_bit=%.3f\n", $tool_new, $bit_new, $bit_hot, $tool_old, $feat_bit );

check( 'new power tool outranks new driver bit', $tool_new > $bit_new );
check( 'a bit many people actually order outranks an untested tool', $bit_hot > $tool_new );
check( 'scores fade with age', $tool_old < $tool_new / 8 );
check( 'Featured boosts a product', $feat_bit > $bit_new * 2.9 );
check( 'price weight is gentle (tool about 2 to 3x a bit)', $R::price_weight( 559 ) / $R::price_weight( 4.99 ) > 2 && $R::price_weight( 559 ) / $R::price_weight( 4.99 ) < 3 );
check( 'one order since launch beats none', $R::new_score( 1, 100, 10, false ) > $R::new_score( 0, 100, 10, false ) );
check( 'missing price does not break scoring', $R::new_score( 2, '', 5, false ) > 0 );
check( 'half-life is 30 days', abs( $R::recency_weight( 30 ) - 0.5 ) < 1e-9 );

exit( $failed ? 1 : 0 );
