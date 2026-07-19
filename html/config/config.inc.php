<?php
    $config['plugins'] = [
	'archive',
	'zipdownload',
        'newmail_notifier',
	'ident_switch',
];
    $config['log_driver'] = 'stdout';
    $config['zipdownload_selection'] = true;
    $config['des_key'] = '8ao8DCVihkcgjei2RuhDlVjf';
    $config['enable_spellcheck'] = true;
    $config['spellcheck_engine'] = 'pspell';
    include(__DIR__ . '/config.docker.inc.php');
    
$config['imap_cache'] = 'db';
$config['messages_cache'] = true;
$config['imap_cache_ttl'] = '10d';
$config['messages_cache_ttl'] = '10d';
$config['prefer_html'] = true;
$config['htmleditor'] = 1;
$config['ident_switch.check_mail'] = false;
$config['ident_switch.notify_check'] = 0;
$config['refresh_interval'] = 300;
$config['show_images'] = 0;
