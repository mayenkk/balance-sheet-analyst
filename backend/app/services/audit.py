from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.models.audit import AuditLog, DataAccessLog
from app.core.config import settings


class AuditService:
    """Service for audit logging and security monitoring"""
    
    async def log_action(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        db: Session = None
    ):
        """Log a user action"""
        
        if not db:
            return
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
        
        db.add(audit_log)
        db.commit()
    
    async def log_data_access(
        self,
        user_id: int,
        company_id: int,
        access_type: str,
        data_type: str,
        record_count: int = 0,
        access_duration_ms: int = 0,
        db: Session = None
    ):
        """Log data access for compliance and monitoring"""
        
        if not db:
            return
        
        access_log = DataAccessLog(
            user_id=user_id,
            company_id=company_id,
            access_type=access_type,
            data_type=data_type,
            record_count=record_count,
            access_duration_ms=access_duration_ms
        )
        
        db.add(access_log)
        db.commit()
    
    def get_user_audit_logs(
        self,
        user_id: int,
        limit: int = 100,
        db: Session = None
    ) -> list:
        """Get audit logs for a specific user"""
        
        if not db:
            return []
        
        logs = db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
        
        return logs
    
    def get_company_access_logs(
        self,
        company_id: int,
        limit: int = 100,
        db: Session = None
    ) -> list:
        """Get data access logs for a specific company"""
        
        if not db:
            return []
        
        logs = db.query(DataAccessLog).filter(
            DataAccessLog.company_id == company_id
        ).order_by(DataAccessLog.created_at.desc()).limit(limit).all()
        
        return logs
    
    def get_security_alerts(
        self,
        db: Session = None
    ) -> list:
        """Get potential security alerts from audit logs"""
        
        if not db:
            return []
        
        # Look for suspicious activities
        alerts = []
        
        # Failed login attempts
        failed_logins = db.query(AuditLog).filter(
            AuditLog.action == "login",
            AuditLog.success == False
        ).order_by(AuditLog.created_at.desc()).limit(10).all()
        
        for login in failed_logins:
            alerts.append({
                "type": "failed_login",
                "user_id": login.user_id,
                "timestamp": login.created_at,
                "details": "Multiple failed login attempts"
            })
        
        # Unusual data access patterns
        high_volume_access = db.query(DataAccessLog).filter(
            DataAccessLog.record_count > 1000
        ).order_by(DataAccessLog.created_at.desc()).limit(10).all()
        
        for access in high_volume_access:
            alerts.append({
                "type": "high_volume_access",
                "user_id": access.user_id,
                "company_id": access.company_id,
                "timestamp": access.created_at,
                "details": f"Accessed {access.record_count} records"
            })
        
        return alerts 