<?php
if (!defined('AIN7_CONFIG_LOADED'))
	require 'ain7_config.php';
?>

<!-- Pied de page du thème du portail AIn7 -->
<div class="footer">
	<p> <a href="<?php echo $ain7_path; ?>rss/">Flux RSS</a> |
		<a href="<?php echo $ain7_path; ?>association/contact/">Contact</a> |
		<a href="<?php echo $ain7_path; ?>apropos/">A propos</a> |
		<a href="<?php echo $ain7_path; ?>mentions_legales/">Mentions legales</a> |
		<a href="http://jigsaw.w3.org/css-validator/check/referer/">XHTML</a><br />
		&copy; Copyright <?php echo date('Y') . ' AIn7 - Version ' . $ain7_version; ?></p>
</div> <!-- fin pied de page portail AIn7 -->


