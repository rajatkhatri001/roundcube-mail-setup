<?php
  $config['db_dsnw'] = 'mysql://roundcube:123@roundcubemail-mysql:3306/roundcubemail';
  $config['db_dsnr'] = '';
  $config['imap_host'] = 'ssl://imap.hostinger.com:993';
  $config['smtp_host'] = 'ssl://smtp.hostinger.com:465';
  $config['username_domain'] = '';
  $config['temp_dir'] = '/tmp/roundcube-temp';
  $config['skin'] = 'elastic';
  $config['request_path'] = '/';
  $config['plugins'] = array_filter(array_unique(array_merge($config['plugins'], ['archive', 'zipdownload', 'ident_switch'])));
  
