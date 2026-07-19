<?php
  $config['db_dsnw'] = 'mysql://roundcube:123@roundcubemail-mysql:3306/roundcubemail';
  $config['db_dsnr'] = '';
  $config['imap_host'] = 'tls://mailproxy:9993:9993';
  $config['smtp_host'] = 'tls://mailproxy:9465:9465';
  $config['username_domain'] = '';
  $config['temp_dir'] = '/tmp/roundcube-temp';
  $config['skin'] = 'elastic';
  $config['request_path'] = '/';
  $config['plugins'] = array_filter(array_unique(array_merge($config['plugins'], ['archive', 'zipdownload', 'newmail_notifier', 'ident_switch'])));
  
