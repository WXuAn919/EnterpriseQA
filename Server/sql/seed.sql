USE db_enterprise_qa;

INSERT INTO sys_user (id, username, real_name, password, role, status)
VALUES
    (1, 'admin', '系统管理员', 'e10adc3949ba59abbe56e057f20f883e', 'admin', 'active'),
    (2, 'zhangsan', '张三', 'e10adc3949ba59abbe56e057f20f883e', 'user', 'active'),
    (3, 'lisi', '李四', 'e10adc3949ba59abbe56e057f20f883e', 'user', 'active');

INSERT INTO kb_knowledge_base (id, name, description, status, created_by)
VALUES
    (1, '企业通用知识库', '用于演示员工制度、IT规范与入职流程的基础知识库。', 'enabled', 1);

INSERT INTO kb_document (id, knowledge_base_id, title, original_name, file_type, file_path, process_status, chunk_count, created_by)
VALUES
    (1, 1, '员工手册', 'employee_handbook.md', 'md', 'Server/sample_docs/employee_handbook.md', 'processed', 2, 1),
    (2, 1, 'IT使用规范', 'it_policy.txt', 'txt', 'Server/sample_docs/it_policy.txt', 'processed', 2, 1),
    (3, 1, '新员工入职说明', 'onboarding_guide.md', 'md', 'Server/sample_docs/onboarding_guide.md', 'processed', 2, 1);

INSERT INTO kb_chunk (document_id, sequence, vector_id, content, char_count, meta_json)
VALUES
    (1, 1, 'doc-1-chunk-1', '公司实行标准五天工作制，日常办公时间为工作日 09:00 至 18:00，中午休息 1 小时。员工请假需要在 OA 系统发起申请并经直属主管审批。', 71, '{"documentTitle":"员工手册","knowledgeBaseId":1,"sequence":1}'),
    (1, 2, 'doc-1-chunk-2', '员工应遵守保密制度，不得擅自向外部人员泄露客户信息、财务数据和内部流程文档。如发现信息安全风险，应立即向行政与信息安全负责人报告。', 72, '{"documentTitle":"员工手册","knowledgeBaseId":1,"sequence":2}'),
    (2, 1, 'doc-2-chunk-1', '公司电脑默认安装统一办公软件，禁止私自安装来源不明的软件。确需安装开发工具时，应向 IT 管理员提交申请并说明用途。', 64, '{"documentTitle":"IT使用规范","knowledgeBaseId":1,"sequence":1}'),
    (2, 2, 'doc-2-chunk-2', '办公账号密码应至少每 90 天修改一次，涉及核心系统的账号不得多人共用。离岗前应锁屏并关闭包含敏感信息的页面。', 58, '{"documentTitle":"IT使用规范","knowledgeBaseId":1,"sequence":2}'),
    (3, 1, 'doc-3-chunk-1', '新员工入职第一天需要完成账号开通、门禁录入、工位确认和制度学习。直属导师将在三天内安排业务系统与流程培训。', 58, '{"documentTitle":"新员工入职说明","knowledgeBaseId":1,"sequence":1}'),
    (3, 2, 'doc-3-chunk-2', '试用期员工每周需提交一次学习周报，试用期结束前由导师和部门负责人联合完成转正评估。', 46, '{"documentTitle":"新员工入职说明","knowledgeBaseId":1,"sequence":2}');

INSERT INTO qa_session (id, user_id, knowledge_base_id, title, last_question_at)
VALUES
    (1, 2, 1, '办公时间是什么？', NOW());

INSERT INTO qa_message (session_id, question, answer, hit_chunks, sources_json, elapsed_ms)
VALUES
    (
        1,
        '公司的日常办公时间是什么？',
        '根据员工手册，公司实行标准五天工作制，工作日办公时间为 09:00 至 18:00，中午休息 1 小时。',
        '公司实行标准五天工作制，日常办公时间为工作日 09:00 至 18:00，中午休息 1 小时。',
        '[{"documentName":"员工手册","source":"employee_handbook.md","chunkId":1,"excerpt":"公司实行标准五天工作制，日常办公时间为工作日 09:00 至 18:00，中午休息 1 小时。"}]',
        320
    );
