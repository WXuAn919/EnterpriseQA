CREATE DATABASE IF NOT EXISTS db_enterprise_qa DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE db_enterprise_qa;

DROP TABLE IF EXISTS qa_message;
DROP TABLE IF EXISTS qa_session;
DROP TABLE IF EXISTS kb_chunk;
DROP TABLE IF EXISTS kb_document;
DROP TABLE IF EXISTS kb_knowledge_base;
DROP TABLE IF EXISTS sys_login_log;
DROP TABLE IF EXISTS sys_user;

CREATE TABLE sys_user (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户主键',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录账号',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    password CHAR(32) NOT NULL COMMENT 'MD5 加密密码',
    role VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色：admin/user',
    status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='系统用户表';

CREATE TABLE sys_login_log (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志主键',
    user_id INT NULL COMMENT '用户主键',
    username VARCHAR(50) NOT NULL COMMENT '登录账号',
    ip_address VARCHAR(64) NULL COMMENT '登录IP',
    status VARCHAR(20) NOT NULL DEFAULT 'success' COMMENT '登录状态',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    CONSTRAINT fk_login_log_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
) COMMENT='用户登录日志表';

CREATE TABLE kb_knowledge_base (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '知识库主键',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '知识库名称',
    description TEXT NULL COMMENT '知识库说明',
    status VARCHAR(20) NOT NULL DEFAULT 'enabled' COMMENT '状态',
    created_by INT NOT NULL COMMENT '创建人',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_kb_user FOREIGN KEY (created_by) REFERENCES sys_user(id)
) COMMENT='知识库主表';

CREATE TABLE kb_document (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '文档主键',
    knowledge_base_id INT NOT NULL COMMENT '所属知识库',
    title VARCHAR(150) NOT NULL COMMENT '文档标题',
    original_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_type VARCHAR(20) NOT NULL COMMENT '文件类型',
    file_path VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    process_status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '处理状态',
    chunk_count INT NOT NULL DEFAULT 0 COMMENT '切片数量',
    created_by INT NOT NULL COMMENT '上传人',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_doc_kb FOREIGN KEY (knowledge_base_id) REFERENCES kb_knowledge_base(id),
    CONSTRAINT fk_doc_user FOREIGN KEY (created_by) REFERENCES sys_user(id)
) COMMENT='知识库文档表';

CREATE TABLE kb_chunk (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '切片主键',
    document_id INT NOT NULL COMMENT '所属文档',
    sequence INT NOT NULL COMMENT '切片序号',
    vector_id VARCHAR(100) NOT NULL UNIQUE COMMENT '向量ID',
    content TEXT NOT NULL COMMENT '切片内容',
    char_count INT NOT NULL COMMENT '字符数',
    meta_json LONGTEXT NULL COMMENT '切片元数据',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_chunk_doc FOREIGN KEY (document_id) REFERENCES kb_document(id)
) COMMENT='知识库切片表';

CREATE TABLE qa_session (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '会话主键',
    user_id INT NOT NULL COMMENT '提问用户',
    knowledge_base_id INT NOT NULL COMMENT '所属知识库',
    title VARCHAR(150) NOT NULL COMMENT '会话标题',
    last_question_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后提问时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES sys_user(id),
    CONSTRAINT fk_session_kb FOREIGN KEY (knowledge_base_id) REFERENCES kb_knowledge_base(id)
) COMMENT='问答会话表';

CREATE TABLE qa_message (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '消息主键',
    session_id INT NOT NULL COMMENT '所属会话',
    question LONGTEXT NOT NULL COMMENT '用户问题',
    answer LONGTEXT NOT NULL COMMENT 'AI 回答',
    hit_chunks LONGTEXT NULL COMMENT '命中片段文本',
    sources_json LONGTEXT NULL COMMENT '引用来源 JSON',
    elapsed_ms INT NOT NULL DEFAULT 0 COMMENT '耗时毫秒',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT fk_message_session FOREIGN KEY (session_id) REFERENCES qa_session(id)
) COMMENT='问答消息表';
