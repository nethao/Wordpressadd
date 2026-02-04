<?php
/*
Plugin Name: 软文广告高级管理系统 (V2.3 审核增强版) - 备份文件
Description: 包含动态栏目指定、精准前端隐藏、状态管理、定时删除、API强制开启及审核通过功能。
Version: 2.3-backup
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
}

function adv_mgr_render_settings() {
    if (isset($_POST['adv_mgr_save'])) {
        update_option('adv_delete_days', intval($_POST['adv_delete_days']));
        update_option('adv_target_category', intval($_POST['adv_target_category']));
        echo '<div class="updated"><p>设置已成功保存！</p></div>';
    }
    
    $days = get_option('adv_delete_days', 45);
    $target_cat = get_option('adv_target_category', 0);
    $categories = get_categories(array('hide_empty' => 0));
    ?>
    <div class="wrap">
        <h1>软文栏目高级设置</h1>
        <form method="post">
            <table class="form-table">
                <tr>
                    <th scope="row">指定发布栏目</th>
                    <td>
                        <select name="adv_target_category">
                            <option value="0">-- 请选择一个分类 --</option>
                            <?php foreach ($categories as $cat): ?>
                                <option value="<?php echo $cat->term_id; ?>" <?php selected($target_cat, $cat->term_id); ?>>
                                    <?php echo $cat->name; ?> (ID: <?php echo $cat->term_id; ?>)
                                </option>
                            <?php endforeach; ?>
                        </select>
                        <?php 
                        if ($target_cat > 0) {
                            $cat_link = get_category_link($target_cat);
                            echo '<p class="description"><b>当前动态访问地址：</b><a href="' . esc_url($cat_link) . '" target="_blank">' . esc_url($cat_link) . '</a></p>';
                        }
                        ?>
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
    </div>
    <?php
}

/**
 * 4. 优化后的前端隐藏逻辑
 * 首页/搜索/小工具排除，但【分类详情页】必须显示内容
 */
add_action('pre_get_posts', 'adv_mgr_exclude_logic');
function adv_mgr_exclude_logic($query) {
    // 1. 后台不拦截，非主查询不拦截（确保不干扰其他功能）
    if (is_admin() || !$query->is_main_query()) return;

    $target_cat = get_option('adv_target_category', 0);
    if ($target_cat <= 0) return;

    // 2. 只有在【不是】访问该分类页面时，才执行排除逻辑
    if ( ! $query->is_category($target_cat) ) {
        
        // 如果是首页、搜索页或其他存档页
        if ($query->is_home() || $query->is_search() || $query->is_archive()) {
            
            // 排除掉该分类下的所有文章
            $query->set('category__not_in', array($target_cat));
            
            // 关键：强制主循环只展示原生文章 'post'，从而在小工具里彻底隐藏 'adv_posts'
            $query->set('post_type', array('post'));
        }
    } else {
        // 3. 当用户主动访问该分类 URL 时，必须允许展示 'adv_posts' 类型
        $query->set('post_type', array('post', 'adv_posts'));
    }
}

/**
 * 5. API 提交自动化与统计
 */
// API提交时自动关联所选分类
add_action('rest_insert_adv_posts', function($post, $request, $creating) {
    if ($creating) {
        $target_cat = get_option('adv_target_category', 0);
        if ($target_cat > 0) wp_set_post_categories($post->ID, array($target_cat));
    }
}, 10, 3);

// 统计显示 - V2.3优化：突出显示待审核文章
add_action('restrict_manage_posts', function() {
    global $typenow;
    if ($typenow == 'adv_posts') {
        $counts = wp_count_posts('adv_posts');
        $pending_style = $counts->pending > 0 ? 'color: #d63638; font-weight: bold;' : '';
        $publish_style = 'color: #00a32a; font-weight: bold;';
        
        echo "<div class='alignleft actions' style='line-height:32px; margin-left:10px;'>";
        echo "📊 统计：";
        echo "<span style='{$publish_style}'>已发布({$counts->publish})</span> | ";
        echo "<span style='{$pending_style}'>待审核({$counts->pending})</span> | ";
        echo "回收站(<b>{$counts->trash}</b>)";
        
        if ($counts->pending > 0) {
            echo " | <span style='color: #d63638;'>⚠️ 有 {$counts->pending} 篇文章待审核</span>";
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

// 其余代码省略，这是备份文件
?>