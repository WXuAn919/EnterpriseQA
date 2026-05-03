"""重建 Chroma 向量索引的脚本。"""

from app import create_app
from app.models import KbDocument
from app.services import DocumentService, VectorStoreService


def main():
    """遍历所有文档并重新执行切片与向量索引。"""

    app = create_app()
    with app.app_context():
        documents = KbDocument.query.order_by(KbDocument.id.asc()).all()
        if not documents:
            print("未找到任何文档记录，无需重建向量索引。")
            return

        for document in documents:
            print(f"开始处理文档：{document.title}")
            DocumentService.split_and_store_chunks(document)
            VectorStoreService.index_document(document)
            print(f"完成处理文档：{document.title}")

        print("所有文档向量索引重建完成。")


if __name__ == "__main__":
    main()
