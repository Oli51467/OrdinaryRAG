import traceback
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from service.document_service import DocumentService
from db.database import get_db
from pydantic import BaseModel

router = APIRouter()

class DocumentBase(BaseModel):
    """文档基本信息"""
    file_name: str
    file_size: int
    upload_time: datetime


class DocumentCreate(DocumentBase):
    """创建文档的请求模型"""
    file_path: str
    id: str


class DocumentResponse(DocumentBase):
    """文档响应模型"""
    id: str
    file_type: str  # 添加文件类型字段
    file_path: Optional[str] = None
    
    class Config:
        from_attributes = True  # 允许直接从ORM模型转换


class DocumentList(BaseModel):
    """文档列表响应模型"""
    documents: List[DocumentResponse] 


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 检查文件类型是否允许
    document_service = DocumentService(db)
    if not document_service.allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
     # 处理文档
    document = document_service.process_document(file)
        
    # 返回文档信息
    return {
        "id": str(document.id),
        "file_name": document.file_name,
        "upload_time": document.upload_time,
        "file_size": document.file_size,
        "file_type": document.file_type
    }


@router.get("/list", response_model=DocumentList)
async def list_documents(db: Session = Depends(get_db)):
    try:
        document_list = DocumentService(db).get_all_documents()     
        
        # 将SQLAlchemy模型对象转换为字典
        documents = []
        for doc in document_list:
            # 直接访问Document对象的属性
            documents.append({
                "id": str(doc.id),
                "file_name": doc.file_name,
                "upload_time": doc.upload_time,
                "file_size": doc.file_size,
                "file_type": doc.file_type,
                "file_path": None  # 或其他适当的默认值
            })
        
        return {"documents": documents}
    except Exception as e:
        error_detail = f"获取文档列表失败: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {str(e)}")


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    try:
        print("delete:" + str(doc_id))
        deleted = DocumentService(db).delete_document(doc_id)
        if deleted:
            return JSONResponse(content={"message": "文档删除成功"}, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="文档不存在")
    except Exception as e:
        error_detail = f"删除文档失败: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}") 