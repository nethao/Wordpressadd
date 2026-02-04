<?php
/*
Plugin Name: 软文广告高级管理系统 (V2.5 头条文章版)
Description: 支持全站点随机栏目发布、头条文章草稿管理、状态管理、定时删除、API强制开启及审核通过功能。新增📋头条文章栏目，专门用于草稿保存和查看。
Version: 2.5
Author: Gemini Thought Partner
*/

if (!defined('ABSPATH')) exit;

/**
 * 1. 核心权限：强制开启本地环境下的应用程序密码功能
 * 解决本地非HTTPS环境下无法生成API密码的问题
 */
add_filter('wp_is_application_passwords_available', '__return_true', 999);
add_filter('wp_is_application_passwords_available_on_http', '__return_true', 999);

/**
 * 2. 注册自定义文章类型 (CPT)
 */
add_action('init', 'adv_mgr_setup_post_type');
function adv_mgr_setup_post_type() {
    register_post_type('adv_posts', array(
        'labels' => array(
            'name' => '软文广告',
            'singular_name' => '软文',
            'menu_name' => '软文管理',
            'add_new' => '发布新软文',
        ),
        'public' => true,
        'show_in_rest' => true, 
        'show_ui' => true,
        'show_in_menu' => true,
        'menu_icon' => 'dashicons-feedback',
        'supports' => array('title', 'editor', 'author'),
        'taxonomies' => array('category'), // 挂载原生分类
        'rewrite' => array(
            'slug' => 'adv-posts',
            'with_front' => false
        ),
    ));
}

/**
 * 动态替换文章链接为ID.htm格式
 */
add_filter('post_type_link', 'adv_mgr_post_type_link', 10, 2);
function adv_mgr_post_type_link($post_link, $post) {
    // 只处理adv_posts类型的文章
    if ($post->post_type === 'adv_posts') {
        // 生成ID.htm格式的链接
        $post_link = home_url('/adv-posts/' . $post->ID . '.htm');
    }
    return $post_link;
}

/**
 * 添加自定义rewrite规则以支持ID.htm格式
 */
add_action('init', 'adv_mgr_add_rewrite_rules', 11);
function adv_mgr_add_rewrite_rules() {
    // 添加rewrite规则：/adv-posts/123.htm -> /index.php?post_type=adv_posts&p=123
    add_rewrite_rule(
        '^adv-posts/([0-9]+)\.htm/?$',
        'index.php?post_type=adv_posts&p=$matches[1]',
        'top'
    );
}

/**
 * 3. 栏目设置页面：支持动态URL获取
 */
add_action('admin_menu', 'adv_mgr_add_setting_page');
function adv_mgr_add_setting_page() {
    add_submenu_page('edit.php?post_type=adv_posts', '栏目设置', '栏目设置', 'manage_options', 'adv_settings', 'adv_mgr_render_settings');
    // 添加随机重分配工具页面
    add_submenu_page('edit.php?post_type=adv_posts', '随机重分配', '随机重分配', 'manage_options', 'adv_redistribute', 'adv_mgr_redistribute_page');
}

function adv_mgr_render_settings() {
    if (isset($_POST['adv_mgr_save'])) {
        update_option('adv_delete_days', intval($_POST['adv_delete_days']));
        update_option('adv_random_publish_enabled', isset($_POST['adv_random_publish_enabled']) ? 1 : 0);
        echo '<div class="updated"><p>设置已成功保存！</p></div>';
    }
    
    $days = get_option('adv_delete_days', 45);
    $random_enabled = get_option('adv_random_publish_enabled', 1); // 默认开启随机发布
    $categories = get_categories(array('hide_empty' => 0));
    ?>
    <div class="wrap">
        <h1>软文栏目高级设置</h1>
        <form method="post">
            <table class="form-table">
                <tr>
                    <th scope="row">随机发布模式</th>
                    <td>
                        <label>
                            <input type="checkbox" name="adv_random_publish_enabled" value="1" <?php checked($random_enabled, 1); ?> />
                            启用全站点随机栏目发布
                        </label>
                        <p class="description">
                            <strong>✅ 已启用随机发布模式</strong><br>
                            • 每篇软文将随机分配到网站的任意栏目<br>
                            • 覆盖全站点所有分类，提高内容分布的自然性<br>
                            • 可用栏目总数：<strong><?php echo count($categories); ?></strong> 个<br>
                            • 栏目列表：<?php 
                            $cat_names = array();
                            foreach ($categories as $cat) {
                                $cat_names[] = $cat->name;
                            }
                            echo implode('、', array_slice($cat_names, 0, 10));
                            if (count($cat_names) > 10) echo '...等';
                            ?>
                        </p>
                    </td>
                </tr>
                <tr>
                    <th scope="row">📋 头条文章设置</th>
                    <td>
                        <p class="description">
                            <strong>🎯 头条文章功能说明</strong><br>
                            • 头条文章分类ID：<strong>16035</strong><br>
                            • 所有头条文章将自动保存为<strong>草稿状态</strong><br>
                            • 头条文章<strong>不会发布到前端</strong>，仅供后台查看和管理<br>
                            • 可通过标题前缀"📋"或"头条"自动识别<br>
                            • 也可通过API参数 <code>headline_article=true</code> 指定
                        </p>
                        <?php
                        // 统计头条文章数量
                        $headline_posts = get_posts(array(
                            'post_type' => 'adv_posts',
                            'post_status' => 'draft',
                            'category' => 16035,
                            'posts_per_page' => -1,
                            'fields' => 'ids'
                        ));
                        $headline_count = count($headline_posts);
                        ?>
                        <p>
                            <strong>当前头条文章数量：</strong>
                            <span style="color: #ff6900; font-weight: bold; font-size: 16px;"><?php echo $headline_count; ?></span> 篇
                            <?php if ($headline_count > 0): ?>
                            <a href="<?php echo admin_url('edit.php?post_type=adv_posts&headline_filter=headline'); ?>" 
                               class="button button-secondary" style="margin-left: 10px;">
                                📋 查看头条文章
                            </a>
                            <?php endif; ?>
                        </p>
                    </td>
                </tr>
                <tr>
                    <th scope="row">定时清理设置</th>
                    <td>
                        <input type="number" name="adv_delete_days" value="<?php echo $days; ?>" /> 天后自动移入回收站
                    </td>
                </tr>
            </table>
            <input type="hidden" name="adv_mgr_save" value="1">
            <?php submit_button(); ?>
        </form>
        
        <!-- 随机发布统计信息 -->
        <div class="card" style="margin-top: 20px; padding: 15px;">
            <h3>📊 随机发布统计</h3>
            <?php
            // 统计各分类下的软文数量
            $category_stats = array();
            foreach ($categories as $cat) {
                $count = get_posts(array(
                    'post_type' => 'adv_posts',
                    'post_status' => 'publish',
                    'category' => $cat->term_id,
                    'posts_per_page' => -1,
                    'fields' => 'ids'
                ));
                if (!empty($count)) {
                    $category_stats[$cat->name] = count($count);
                }
            }
            
            if (!empty($category_stats)) {
                echo '<p><strong>当前各栏目软文分布：</strong></p>';
                echo '<ul>';
                foreach ($category_stats as $cat_name => $count) {
                    echo "<li>{$cat_name}：{$count} 篇</li>";
                }
                echo '</ul>';
            } else {
                echo '<p>暂无已发布的软文数据</p>';
            }
            ?>
        </div>
    </div>
    <?php
}

/**
 * 随机重分配工具页面
 */
function adv_mgr_redistribute_page() {
    // 处理重分配请求
    if (isset($_POST['redistribute_all'])) {
        $redistributed_count = adv_mgr_redistribute_all_posts();
        echo '<div class="updated"><p>✅ 重分配完成！共处理了 ' . $redistributed_count . ' 篇文章。</p></div>';
    }
    
    // 获取当前软文统计
    $published_posts = get_posts(array(
        'post_type' => 'adv_posts',
        'post_status' => 'publish',
        'posts_per_page' => -1,
        'fields' => 'ids'
    ));
    
    $categories = get_categories(array('hide_empty' => 0));
    
    ?>
    <div class="wrap">
        <h1>🎲 随机重分配工具</h1>
        
        <div class="card" style="margin-top: 20px; padding: 20px;">
            <h3>📊 当前状态</h3>
            <p><strong>已发布软文总数：</strong><?php echo count($published_posts); ?> 篇</p>
            <p><strong>可用栏目总数：</strong><?php echo count($categories); ?> 个</p>
            
            <?php if (!empty($published_posts)): ?>
            <form method="post" onsubmit="return confirm('确定要重新随机分配所有已发布软文的栏目吗？此操作不可撤销。');">
                <p class="description">
                    <strong>⚠️ 重要说明：</strong><br>
                    • 此操作将重新随机分配所有已发布软文的栏目<br>
                    • 每篇文章将被随机分配到任意一个栏目中<br>
                    • 操作不可撤销，请谨慎使用<br>
                    • 建议在非高峰时段执行此操作
                </p>
                
                <input type="hidden" name="redistribute_all" value="1">
                <button type="submit" class="button button-primary button-large" style="margin-top: 15px;">
                    🎲 开始随机重分配所有软文
                </button>
            </form>
            <?php else: ?>
            <p style="color: #666;">暂无已发布的软文需要重分配。</p>
            <?php endif; ?>
        </div>
        
        <!-- 分类分布预览 -->
        <div class="card" style="margin-top: 20px; padding: 20px;">
            <h3>📈 当前栏目分布</h3>
            <?php
            $category_distribution = array();
            foreach ($categories as $cat) {
                $count = get_posts(array(
                    'post_type' => 'adv_posts',
                    'post_status' => 'publish',
                    'category' => $cat->term_id,
                    'posts_per_page' => -1,
                    'fields' => 'ids'
                ));
                $category_distribution[$cat->name] = count($count);
            }
            
            if (array_sum($category_distribution) > 0) {
                echo '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 15px;">';
                foreach ($category_distribution as $cat_name => $count) {
                    $percentage = count($published_posts) > 0 ? round(($count / count($published_posts)) * 100, 1) : 0;
                    echo '<div style="padding: 10px; background: #f9f9f9; border-radius: 4px; text-align: center;">';
                    echo '<strong>' . esc_html($cat_name) . '</strong><br>';
                    echo '<span style="font-size: 18px; color: #0073aa;">' . $count . '</span> 篇<br>';
                    echo '<small>(' . $percentage . '%)</small>';
                    echo '</div>';
                }
                echo '</div>';
            } else {
                echo '<p style="color: #666;">暂无数据</p>';
            }
            ?>
        </div>
    </div>
    <?php
}

/**
 * 执行所有软文的随机重分配（排除头条文章）
 */
function adv_mgr_redistribute_all_posts() {
    // 获取所有已发布的软文（排除头条文章分类）
    $posts = get_posts(array(
        'post_type' => 'adv_posts',
        'post_status' => 'publish',
        'posts_per_page' => -1,
        'category__not_in' => array(16035) // 排除头条文章分类
    ));
    
    // 获取所有可用分类（排除未分类和头条文章）
    $categories = get_categories(array(
        'hide_empty' => 0,
        'exclude' => array(1, 16035) // 排除未分类和头条文章
    ));
    
    if (empty($categories)) {
        return 0;
    }
    
    $redistributed_count = 0;
    
    foreach ($posts as $post) {
        // 随机选择一个分类
        $random_category = $categories[array_rand($categories)];
        
        // 更新文章分类
        $result = wp_set_post_categories($post->ID, array($random_category->term_id));
        
        if ($result !== false) {
            $redistributed_count++;
            
            // 记录重分配日志
            error_log("软文随机重分配: 文章ID={$post->ID}, 标题={$post->post_title}, 重新分配到={$random_category->name}(ID:{$random_category->term_id})");
        }
    }
    
    return $redistributed_count;
}

/**
 * 4. 移除前端隐藏逻辑 - 随机发布模式下不需要隐藏特定分类
 * 软文将随机分布在各个栏目中，与普通文章混合显示
 * 头条文章（ID=16035）只保存为草稿，不会在前端显示
 */
add_action('pre_get_posts', 'adv_mgr_random_display_logic');
function adv_mgr_random_display_logic($query) {
    // 后台管理页面的头条文章筛选逻辑
    if (is_admin() && $query->is_main_query()) {
        global $pagenow, $typenow;
        
        if ($pagenow == 'edit.php' && $typenow == 'adv_posts') {
            // 检查是否筛选头条文章
            if (isset($_GET['headline_filter']) && $_GET['headline_filter'] == 'headline') {
                // 只显示头条文章（分类ID=16035，状态为草稿）
                $query->set('category', 16035);
                $query->set('post_status', 'draft');
            } else {
                // 默认显示所有文章，不进行分类排除
                // 移除之前的排除逻辑，让管理员可以看到所有文章
            }
        }
        return;
    }
    
    // 前端显示逻辑：排除头条文章分类
    if (!is_admin() && $query->is_main_query()) {
        // 在所有页面类型中都允许显示 adv_posts 类型的文章，但排除头条文章
        if ($query->is_home() || $query->is_search() || $query->is_archive() || $query->is_category()) {
            $post_types = $query->get('post_type');
            if (empty($post_types)) {
                $post_types = array('post');
            }
            if (!is_array($post_types)) {
                $post_types = array($post_types);
            }
            
            // 添加 adv_posts 到查询的文章类型中
            if (!in_array('adv_posts', $post_types)) {
                $post_types[] = 'adv_posts';
                $query->set('post_type', $post_types);
            }
            
            // 排除头条文章分类（ID=16035）
            $excluded_cats = $query->get('category__not_in');
            if (empty($excluded_cats)) {
                $excluded_cats = array();
            }
            if (!in_array(16035, $excluded_cats)) {
                $excluded_cats[] = 16035;
                $query->set('category__not_in', $excluded_cats);
            }
        }
    }
}

/**
 * 5. API 提交自动化与统计 - 随机分类分配和头条文章处理
 */
// API提交时自动随机分配分类或处理头条文章
add_action('rest_insert_adv_posts', function($post, $request, $creating) {
    if ($creating) {
        $random_enabled = get_option('adv_random_publish_enabled', 1);
        
        // 检查是否为头条文章（通过请求参数或标题判断）
        $is_headline = false;
        
        // 方法1：通过API请求参数判断
        if ($request->get_param('headline_article')) {
            $is_headline = true;
            error_log("头条文章识别: 通过API参数 headline_article=true");
        }
        
        // 方法2：通过分类判断（如果包含16035分类）
        $categories = $request->get_param('categories');
        if (is_array($categories) && in_array(16035, $categories)) {
            $is_headline = true;
            error_log("头条文章识别: 通过分类ID 16035");
        }
        
        // 方法3：通过标题前缀判断（如果标题以"📋"或"头条"开头）
        $title = $post->post_title;
        if (strpos($title, '📋') === 0 || strpos($title, '头条') === 0) {
            $is_headline = true;
            error_log("头条文章识别: 通过标题前缀");
        }
        
        // 记录调试信息
        error_log("文章创建调试: 标题={$title}, 是否头条={$is_headline}, 请求参数=" . json_encode($request->get_params()));
        
        if ($is_headline) {
            // 头条文章：分配到指定分类并保持草稿状态
            wp_set_post_categories($post->ID, array(16035));
            
            // 确保文章状态为草稿
            wp_update_post(array(
                'ID' => $post->ID,
                'post_status' => 'draft'
            ));
            
            // 记录头条文章日志
            error_log("头条文章创建成功: 文章ID={$post->ID}, 标题={$title}, 状态=草稿, 分类=头条文章(ID:16035)");
            
        } else if ($random_enabled) {
            // 普通软文：随机分配分类
            $categories = get_categories(array(
                'hide_empty' => 0,
                'exclude' => array(1, 16035) // 排除"未分类"和"头条文章"分类
            ));
            
            if (!empty($categories)) {
                // 随机选择一个分类
                $random_category = $categories[array_rand($categories)];
                wp_set_post_categories($post->ID, array($random_category->term_id));
                
                // 记录随机分配日志
                error_log("软文随机分类分配: 文章ID={$post->ID}, 分配到分类={$random_category->name}(ID:{$random_category->term_id})");
            } else {
                // 如果没有可用分类，分配到默认分类
                wp_set_post_categories($post->ID, array(1));
                error_log("软文分类分配: 文章ID={$post->ID}, 无可用分类，分配到默认分类");
            }
        }
    }
}, 10, 3);

// 统计显示 - V2.4优化：添加头条文章栏目和统计信息
add_action('restrict_manage_posts', function() {
    global $typenow;
    if ($typenow == 'adv_posts') {
        $counts = wp_count_posts('adv_posts');
        
        // 统计头条文章数量（分类ID=16035的草稿文章）
        $headline_count = get_posts(array(
            'post_type' => 'adv_posts',
            'post_status' => 'draft',
            'category' => 16035,
            'posts_per_page' => -1,
            'fields' => 'ids'
        ));
        $headline_total = count($headline_count);
        
        $pending_style = $counts->pending > 0 ? 'color: #d63638; font-weight: bold;' : '';
        $publish_style = 'color: #00a32a; font-weight: bold;';
        $headline_style = 'color: #ff6900; font-weight: bold;';
        
        echo "<div class='alignleft actions' style='line-height:32px; margin-left:10px;'>";
        echo "📊 统计：";
        echo "<span style='{$publish_style}'>已发布({$counts->publish})</span> | ";
        echo "<span style='{$pending_style}'>待审核({$counts->pending})</span> | ";
        echo "<span style='{$headline_style}'>📋头条文章({$headline_total})</span> | ";
        echo "回收站(<b>{$counts->trash}</b>)";
        
        if ($counts->pending > 0) {
            echo " | <span style='color: #d63638;'>⚠️ 有 {$counts->pending} 篇文章待审核</span>";
        }
        echo "</div>";
        
        // 添加头条文章筛选按钮
        echo "<div class='alignleft actions' style='margin-left:10px;'>";
        
        // 检查当前是否在筛选头条文章
        $current_filter = isset($_GET['headline_filter']) ? $_GET['headline_filter'] : '';
        
        if ($current_filter == 'headline') {
            // 当前正在查看头条文章，显示"查看全部"按钮
            $all_url = remove_query_arg('headline_filter');
            echo "<a href='{$all_url}' class='button'>查看全部文章</a>";
            echo "<span style='margin-left:10px; color:#ff6900; font-weight:bold;'>📋 当前显示：头条文章</span>";
        } else {
            // 显示"查看头条文章"按钮
            $headline_url = add_query_arg('headline_filter', 'headline');
            echo "<a href='{$headline_url}' class='button button-primary' style='background:#ff6900; border-color:#ff6900;'>📋 查看头条文章</a>";
        }
        
        echo "</div>";
    }
});

/**
 * 6. 定时清理任务和数据库表创建
 */
register_activation_hook(__FILE__, function() {
    // 1. 创建定时清理任务
    if (!wp_next_scheduled('adv_mgr_daily_cleanup')) {
        wp_schedule_event(time(), 'daily', 'adv_mgr_daily_cleanup');
    }
    
    // 2. 创建发稿日志表（用于永久统计）
    global $wpdb;
    $table_name = $wpdb->prefix . 'adv_publish_log';
    $charset_collate = $wpdb->get_charset_collate();
    
    $sql = "CREATE TABLE IF NOT EXISTS $table_name (
        id bigint(20) NOT NULL AUTO_INCREMENT,
        post_id bigint(20) NOT NULL,
        post_title text NOT NULL,
        publish_date datetime DEFAULT CURRENT_TIMESTAMP NOT NULL,
        operator_user varchar(100) DEFAULT '' NOT NULL,
        PRIMARY KEY (id),
        KEY post_id (post_id),
        KEY publish_date (publish_date)
    ) $charset_collate;";
    
    require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
    dbDelta($sql);
    
    // 3. 刷新rewrite规则
    flush_rewrite_rules();
    
    // 记录插件激活日志
    error_log("WordPress软文管理插件V2.4激活成功，日志表已创建，rewrite规则已刷新");
});
add_action('adv_mgr_daily_cleanup', function() {
    $days = get_option('adv_delete_days', 45);
    if ($days <= 0) return;
    $posts = get_posts(array('post_type'=>'adv_posts','posts_per_page'=>-1,'date_query'=>array(array('before'=>"$days days ago")),'fields'=>'ids'));
    foreach ($posts as $id) wp_trash_post($id);
});
/**
 * 强行绕过 REST API 发布权限检查并兼容旧版 WP 方法
 * 修复 Call to undefined method WP_REST_Request::get_path() 错误
 * 生产环境版本：移除临时授权逻辑，使用正确的权限验证
 */
add_filter('rest_pre_dispatch', function($result, $server, $request) {
    // 1. 兼容性获取当前请求的路由
    $route = method_exists($request, 'get_route') ? $request->get_route() : (method_exists($request, 'get_path') ? $request->get_path() : '');

    // 2. 如果是向我们的自定义文章类型发送 POST 请求
    if ($request->get_method() == 'POST' && strpos($route, '/wp/v2/adv_posts') !== false) {
        // 3. 生产环境：确保用户已正确认证
        // 移除了wp_set_current_user(1)临时授权逻辑
        // 现在依赖正确的WordPress认证机制
        if (!is_user_logged_in() && !current_user_can('edit_posts')) {
            return new WP_Error('rest_cannot_create', '您没有权限创建文章', array('status' => 401));
        }
    }
    return $result;
}, 10, 3);

/**
 * 7. 审核通过功能 - V2.3新增
 * 包含单篇审核通过快捷键和批量审核通过功能
 */

// 添加单篇审核通过快捷键
add_filter('post_row_actions', 'adv_mgr_add_approve_action', 10, 2);
function adv_mgr_add_approve_action($actions, $post) {
    // 只在软文管理列表页显示，且文章状态为pending
    if ($post->post_type == 'adv_posts' && $post->post_status == 'pending') {
        $approve_url = wp_nonce_url(
            admin_url('admin.php?action=adv_approve_single&post_id=' . $post->ID),
            'adv_approve_single_' . $post->ID
        );
        
        $actions['adv_approve'] = sprintf(
            '<a href="%s" style="color: #00a32a; font-weight: bold;" title="审核通过此文章">✅ 审核通过</a>',
            $approve_url
        );
    }
    return $actions;
}

// 处理单篇审核通过
add_action('admin_action_adv_approve_single', 'adv_mgr_handle_single_approve');
function adv_mgr_handle_single_approve() {
    // 验证权限和nonce
    if (!current_user_can('edit_posts')) {
        wp_die('您没有权限执行此操作');
    }
    
    $post_id = intval($_GET['post_id']);
    if (!wp_verify_nonce($_GET['_wpnonce'], 'adv_approve_single_' . $post_id)) {
        wp_die('安全验证失败');
    }
    
    // 更新文章状态为已发布
    $result = wp_update_post(array(
        'ID' => $post_id,
        'post_status' => 'publish'
    ));
    
    if ($result) {
        // 记录到永久日志表 - 关键INSERT语句
        global $wpdb;
        $log_table = $wpdb->prefix . 'adv_publish_log';
        $post_title = get_the_title($post_id);
        $current_user = wp_get_current_user();
        $operator = $current_user ? $current_user->user_login : 'system';
        
        // 防止重复记录
        $exists = $wpdb->get_var($wpdb->prepare(
            "SELECT id FROM $log_table WHERE post_id = %d", 
            $post_id
        ));
        
        if (!$exists) {
            $wpdb->insert($log_table, array(
                'post_id' => $post_id,
                'post_title' => $post_title,
                'operator_user' => $operator
            ));
        }
        
        // 记录操作日志
        error_log("软文审核通过: ID={$post_id}, 标题={$post_title}, 操作人={$operator}");
        
        // 重定向回列表页并显示成功消息
        wp_redirect(add_query_arg(array(
            'post_type' => 'adv_posts',
            'adv_approved' => 1
        ), admin_url('edit.php')));
    } else {
        wp_redirect(add_query_arg(array(
            'post_type' => 'adv_posts',
            'adv_error' => 1
        ), admin_url('edit.php')));
    }
    exit;
}

// 添加批量审核通过功能到下拉菜单
add_filter('bulk_actions-edit-adv_posts', 'adv_mgr_add_bulk_approve');
function adv_mgr_add_bulk_approve($bulk_actions) {
    $bulk_actions['adv_bulk_approve'] = '✅ 批量审核通过';
    return $bulk_actions;
}

// 处理批量审核通过
add_filter('handle_bulk_actions-edit-adv_posts', 'adv_mgr_handle_bulk_approve', 10, 3);
function adv_mgr_handle_bulk_approve($redirect_to, $doaction, $post_ids) {
    if ($doaction !== 'adv_bulk_approve') {
        return $redirect_to;
    }
    
    // 验证权限
    if (!current_user_can('edit_posts')) {
        return $redirect_to;
    }
    
    $approved_count = 0;
    $current_user = wp_get_current_user();
    $operator = $current_user ? $current_user->user_login : 'system';
    
    // 获取日志表
    global $wpdb;
    $log_table = $wpdb->prefix . 'adv_publish_log';
    
    foreach ($post_ids as $post_id) {
        $post = get_post($post_id);
        
        // 只处理pending状态的adv_posts
        if ($post && $post->post_type == 'adv_posts' && $post->post_status == 'pending') {
            $result = wp_update_post(array(
                'ID' => $post_id,
                'post_status' => 'publish'
            ));
            
            if ($result) {
                $approved_count++;
                
                // 记录到永久日志表 - 关键INSERT语句
                $post_title = get_the_title($post_id);
                
                // 防止重复记录
                $exists = $wpdb->get_var($wpdb->prepare(
                    "SELECT id FROM $log_table WHERE post_id = %d", 
                    $post_id
                ));
                
                if (!$exists) {
                    $wpdb->insert($log_table, array(
                        'post_id' => $post_id,
                        'post_title' => $post_title,
                        'operator_user' => $operator
                    ));
                }
                
                // 记录操作日志
                error_log("软文批量审核通过: ID={$post_id}, 标题={$post_title}, 操作人={$operator}");
            }
        }
    }
    
    // 重定向并显示结果
    $redirect_to = add_query_arg(array(
        'adv_bulk_approved' => $approved_count
    ), $redirect_to);
    
    return $redirect_to;
}

// 显示审核操作结果消息
add_action('admin_notices', 'adv_mgr_show_approve_notices');
function adv_mgr_show_approve_notices() {
    global $pagenow, $typenow;
    
    // 只在软文管理列表页显示
    if ($pagenow == 'edit.php' && $typenow == 'adv_posts') {
        
        // 单篇审核成功
        if (isset($_GET['adv_approved']) && $_GET['adv_approved'] == 1) {
            echo '<div class="notice notice-success is-dismissible">';
            echo '<p><strong>✅ 审核通过成功！</strong> 文章已发布并计入发稿统计。</p>';
            echo '</div>';
        }
        
        // 单篇审核失败
        if (isset($_GET['adv_error']) && $_GET['adv_error'] == 1) {
            echo '<div class="notice notice-error is-dismissible">';
            echo '<p><strong>❌ 审核失败！</strong> 请重试或联系管理员。</p>';
            echo '</div>';
        }
        
        // 批量审核结果
        if (isset($_GET['adv_bulk_approved'])) {
            $count = intval($_GET['adv_bulk_approved']);
            if ($count > 0) {
                echo '<div class="notice notice-success is-dismissible">';
                echo '<p><strong>✅ 批量审核完成！</strong> 成功审核通过 ' . $count . ' 篇文章，已计入发稿统计。</p>';
                echo '</div>';
            } else {
                echo '<div class="notice notice-warning is-dismissible">';
                echo '<p><strong>⚠️ 批量审核完成！</strong> 没有找到可审核的待审核文章。</p>';
                echo '</div>';
            }
        }
    }
}

/**
 * 11. 注册发稿统计子菜单
 */
add_action('admin_menu', function() {
    add_submenu_page(
        'edit.php?post_type=adv_posts',
        '发稿统计',
        '发稿统计',
        'manage_options',
        'adv-stats',
        'adv_mgr_stats_page'
    );
});

/**
 * 12. 统计页面显示逻辑 - 基于永久日志表
 */
function adv_mgr_stats_page() {
    // 获取日期筛选参数（默认本月）
    $start_date = isset($_GET['start_date']) ? sanitize_text_field($_GET['start_date']) : date('Y-m-01');
    $end_date = isset($_GET['end_date']) ? sanitize_text_field($_GET['end_date']) : date('Y-m-d');
    
    // 快捷日期选择处理
    $preset = isset($_GET['preset']) ? sanitize_text_field($_GET['preset']) : '';
    if ($preset == 'today') {
        $start_date = $end_date = date('Y-m-d');
    } elseif ($preset == 'week') {
        $start_date = date('Y-m-d', strtotime('monday this week'));
        $end_date = date('Y-m-d', strtotime('sunday this week'));
    } elseif ($preset == 'month') {
        $start_date = date('Y-m-01');
        $end_date = date('Y-m-t');
    }

    // 查询已审核通过的文章总数 - 从日志表读取，不受文章删除影响
    global $wpdb;
    $log_table = $wpdb->prefix . 'adv_publish_log';
    
    $count = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(id) FROM $log_table 
         WHERE publish_date >= %s 
         AND publish_date <= %s",
        $start_date . ' 00:00:00',
        $end_date . ' 23:59:59'
    ));

    // 获取当前月份统计（用于对比Python中间件）
    $current_month_start = date('Y-m-01');
    $current_month_end = date('Y-m-t');
    $current_month_count = $wpdb->get_var($wpdb->prepare(
        "SELECT COUNT(id) FROM $log_table 
         WHERE publish_date >= %s 
         AND publish_date <= %s",
        $current_month_start . ' 00:00:00',
        $current_month_end . ' 23:59:59'
    ));

    ?>
    <div class="wrap">
        <h1>📊 发稿统计报表</h1>
        <div class="card" style="max-width: 100%; margin-top: 20px; padding: 20px;">
            
            <!-- 快捷日期选择 -->
            <div style="margin-bottom: 15px;">
                <strong>快捷选择：</strong>
                <a href="?post_type=adv_posts&page=adv-stats&preset=today" class="button <?php echo ($preset == 'today') ? 'button-primary' : ''; ?>">今日</a>
                <a href="?post_type=adv_posts&page=adv-stats&preset=week" class="button <?php echo ($preset == 'week') ? 'button-primary' : ''; ?>">本周</a>
                <a href="?post_type=adv_posts&page=adv-stats&preset=month" class="button <?php echo ($preset == 'month') ? 'button-primary' : ''; ?>">本月</a>
            </div>
            
            <!-- 自定义日期范围 -->
            <form method="get" style="margin-bottom: 20px;">
                <input type="hidden" name="post_type" value="adv_posts">
                <input type="hidden" name="page" value="adv-stats">
                <strong>自定义范围：</strong>
                <input type="date" name="start_date" value="<?php echo esc_attr($start_date); ?>"> 至 
                <input type="date" name="end_date" value="<?php echo esc_attr($end_date); ?>">
                <button type="submit" class="button button-primary">筛选统计</button>
            </form>
            
            <hr>
            
            <!-- 统计结果展示 -->
            <div style="display: flex; gap: 20px; margin-top: 20px; flex-wrap: wrap;">
                
                <!-- 当前筛选范围统计 -->
                <div style="background: #f0f6fb; padding: 20px; border-radius: 8px; flex: 1; min-width: 250px; border-left: 4px solid #2271b1;">
                    <h3 style="margin-top:0; color: #2271b1;">📈 筛选范围发稿量</h3>
                    <div style="font-size: 32px; font-weight: bold; color: #2271b1; margin: 10px 0;"><?php echo $count; ?></div>
                    <div style="color: #666; font-size: 14px;">
                        <?php echo $start_date; ?> 至 <?php echo $end_date; ?>
                    </div>
                </div>
                
                <!-- 本月总计（与Python中间件对比） -->
                <div style="background: #f6f7f7; padding: 20px; border-radius: 8px; flex: 1; min-width: 250px; border-left: 4px solid #50575e;">
                    <h3 style="margin-top:0; color: #50575e;">📊 本月总发稿量</h3>
                    <div style="font-size: 32px; font-weight: bold; color: #50575e; margin: 10px 0;"><?php echo $current_month_count; ?></div>
                    <div style="color: #666; font-size: 14px;">
                        基于审核日志，永久可追溯
                    </div>
                </div>
                
                <!-- 日志表状态 -->
                <?php 
                $total_logs = $wpdb->get_var("SELECT COUNT(id) FROM $log_table");
                $latest_log = $wpdb->get_row("SELECT post_title, publish_date, operator_user FROM $log_table ORDER BY publish_date DESC LIMIT 1");
                ?>
                <div style="background: #f0f9ff; padding: 20px; border-radius: 8px; flex: 1; min-width: 250px; border-left: 4px solid #0ea5e9;">
                    <h3 style="margin-top:0; color: #0ea5e9;">📝 日志表状态</h3>
                    <div style="font-size: 32px; font-weight: bold; color: #0ea5e9; margin: 10px 0;"><?php echo $total_logs; ?></div>
                    <div style="color: #666; font-size: 14px;">
                        总审核记录数
                        <?php if ($latest_log): ?>
                        <br>最新：<?php echo esc_html($latest_log->post_title); ?>
                        <br>时间：<?php echo $latest_log->publish_date; ?>
                        <?php endif; ?>
                    </div>
                </div>
                
            </div>
            
            <!-- 数据说明 -->
            <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;">
                <h4 style="margin-top: 0; color: #856404;">📋 统计规则说明</h4>
                <ul style="margin: 0; color: #856404;">
                    <li><strong>统计对象：</strong>所有通过审核的软文（从pending变为publish状态的文章）</li>
                    <li><strong>数据来源：</strong>基于审核日志表（adv_publish_log），不受文章删除影响</li>
                    <li><strong>核心逻辑：</strong>即使文章45天后被自动删除，依然计入有效稿件统计</li>
                    <li><strong>时间基准：</strong>以审核通过时间为准，确保结算数据的准确性</li>
                    <li><strong>数据一致性：</strong>与Python中间件的"本月发布计数"逻辑完全一致</li>
                    <li><strong>结算保障：</strong>专为结算设计，确保数据永久可追溯</li>
                </ul>
            </div>
            
        </div>
    </div>
    <?php
}
