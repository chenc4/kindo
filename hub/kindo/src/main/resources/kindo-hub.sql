SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `accounts`
-- ----------------------------
DROP TABLE IF EXISTS `accounts`;
CREATE TABLE `accounts` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(32) DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `username_idx` (`username`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for `images`
-- ----------------------------
DROP TABLE IF EXISTS `images`;
CREATE TABLE `images` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `pusher` varchar(255) DEFAULT NULL,
  `version` varchar(255) DEFAULT '1.0',
  `website` varchar(255) DEFAULT NULL,
  `summary` text,
  `license` varchar(25) DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  `size` float unsigned DEFAULT NULL,
  `code` char(6) DEFAULT NULL,
  `unique_name` varchar(255) DEFAULT NULL,
  `buildversion` tinyint(4) DEFAULT '1',
  `buildtime` datetime DEFAULT NULL,
  `createtime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `unique_name_idx` (`unique_name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
