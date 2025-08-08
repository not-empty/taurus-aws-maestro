CREATE DATABASE taurus_maestro;

CREATE TABLE queue_logs (
    id CHAR(26) PRIMARY KEY,
    execution_id CHAR(26) NOT NULL,
    queue_name VARCHAR(100) NOT NULL,
    waiting INT(11) NOT NULL,
    active INT(11) NOT NULL,
    paused INT(11) NOT NULL,
    is_paused TINYINT(1) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_queue_name (queue_name) USING BTREE,
    INDEX idx_execution_id (execution_id) USING BTREE,
    INDEX idx_created_at (created_at) USING BTREE
);

CREATE TABLE ec2_logs (
    id CHAR(26) PRIMARY KEY,
    execution_id CHAR(26) NOT NULL,
    queue_name VARCHAR(100) NOT NULL,
    instance_id VARCHAR(100) NOT NULL,
    status TINYINT(1) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_queue_name (queue_name) USING BTREE,
    INDEX idx_instance_id (instance_id) USING BTREE,
    INDEX idx_execution_id (execution_id) USING BTREE,
    INDEX idx_created_at (created_at) USING BTREE
);

CREATE TABLE aws_action_logs (
    id CHAR(26) PRIMARY KEY,
    execution_id CHAR(26) NOT NULL,
    queue_name VARCHAR(100) NOT NULL,
    instance_id VARCHAR(100) NOT NULL,
    action TINYINT(1) NOT NULL, -- 0 to stopping or 1 to starting
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_queue_name (queue_name) USING BTREE,
    INDEX idx_instance_id (instance_id) USING BTREE,
    INDEX idx_execution_id (execution_id) USING BTREE,
    INDEX idx_action (action) USING BTREE,
    INDEX idx_created_at (created_at) USING BTREE
);

CREATE TABLE queue_action_logs (
    id CHAR(26) PRIMARY KEY,
    execution_id CHAR(26) NOT NULL,
    queue_name VARCHAR(100) NOT NULL,
    action TINYINT(1) NOT NULL, -- 0 to pausing or 1 to resuming
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_queue_name (queue_name) USING BTREE,
    INDEX idx_execution_id (execution_id) USING BTREE,
    INDEX idx_action (action) USING BTREE,
    INDEX idx_created_at (created_at) USING BTREE
);