function birdwise_single_field_report_template_content($content) {
    if (is_admin() || !is_singular('field_report') || !in_the_loop() || !is_main_query()) {
        return $content;
    }

    $post_id = get_the_ID();

    $observation_date = function_exists('get_field') ? get_field('observation_date', $post_id) : '';
    $location = function_exists('get_field') ? get_field('location', $post_id) : '';
    $main_species = function_exists('get_field') ? get_field('main_species', $post_id) : '';
    $short_summary = function_exists('get_field') ? get_field('short_summary', $post_id) : '';
    $field_conditions = function_exists('get_field') ? get_field('field_conditions', $post_id) : '';
    $key_observations = function_exists('get_field') ? get_field('key_observations', $post_id) : '';

    $categories = get_the_terms($post_id, 'report_category') ?: [];
    $regions = get_the_terms($post_id, 'report_region') ?: [];
    $all_terms = array_merge($categories, $regions);

    ob_start();
    ?>

    <article class="bw-single-report bw-single-report-v2">

        <section class="bw-single-report-hero bw-single-report-hero-bg">
            <?php if (has_post_thumbnail()) : ?>
                <div class="bw-single-report-hero-media">
                    <?php the_post_thumbnail('full'); ?>
                </div>
            <?php endif; ?>

            <div class="bw-single-report-hero-inner">
                <div class="bw-single-report-hero-copy">
                    <p class="bw-kicker">Field Report</p>
                    <h1><?php the_title(); ?></h1>

                    <?php if ($short_summary) : ?>
                        <p class="bw-report-lead"><?php echo esc_html($short_summary); ?></p>
                    <?php elseif (has_excerpt()) : ?>
                        <p class="bw-report-lead"><?php echo esc_html(get_the_excerpt()); ?></p>
                    <?php endif; ?>
                </div>

                <aside class="bw-report-hero-details">
                    <h3>Report details</h3>

                    <?php if ($observation_date) : ?>
                        <div><strong>Observation date</strong><span><?php echo esc_html($observation_date); ?></span></div>
                    <?php endif; ?>

                    <?php if ($location) : ?>
                        <div><strong>Location</strong><span><?php echo esc_html($location); ?></span></div>
                    <?php endif; ?>

                    <?php if ($main_species) : ?>
                        <div><strong>Main species</strong><span><?php echo esc_html($main_species); ?></span></div>
                    <?php endif; ?>

                    <?php if (!empty($regions)) : ?>
                        <div><strong>Region</strong><span><?php echo esc_html(implode(', ', wp_list_pluck($regions, 'name'))); ?></span></div>
                    <?php endif; ?>

                    <?php if (!empty($categories)) : ?>
                        <div><strong>Category</strong><span><?php echo esc_html(implode(', ', wp_list_pluck($categories, 'name'))); ?></span></div>
                    <?php endif; ?>

                    <a class="bw-report-back-btn" href="/field-reports/">Back to field reports</a>
                </aside>
            </div>
        </section>

        <section class="bw-single-report-body">
            <div class="bw-single-report-content">

                <div class="bw-report-main">
                    <h2>Field note</h2>
                    <div class="bw-report-content-text">
                        <?php echo wp_kses_post($content); ?>
                    </div>

                    <?php if ($field_conditions) : ?>
                        <h2>Field conditions</h2>
                        <p><?php echo nl2br(esc_html($field_conditions)); ?></p>
                    <?php endif; ?>

                    <?php if ($key_observations) : ?>
                        <h2>Key observations</h2>
                        <ul class="bw-report-observations">
                            <?php
                            $items = preg_split('/\r\n|\r|\n/', trim($key_observations));
                            foreach ($items as $item) {
                                if (trim($item)) {
                                    echo '<li>' . esc_html(trim($item)) . '</li>';
                                }
                            }
                            ?>
                        </ul>
                    <?php endif; ?>

                    <?php if (!empty($all_terms)) : ?>
                        <section class="bw-report-taxonomy">
                            <h2>Field note themes</h2>
                            <div class="bw-report-taxonomy-list">
                                <?php
                                foreach ($all_terms as $term) {
                                    echo '<span>' . esc_html($term->name) . '</span>';
                                }
                                ?>
                            </div>
                        </section>
                    <?php endif; ?>
                </div>

            </div>
        </section>

    </article>

    <?php
    return ob_get_clean();
}
add_filter('the_content', 'birdwise_single_field_report_template_content', 20);
