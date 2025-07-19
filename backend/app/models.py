from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    github_url: HttpUrl
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StudentBase(BaseModel):
    name: str
    github_username: Optional[str] = None
    email: Optional[str] = None
    project_id: Optional[int] = None


class StudentCreate(StudentBase):
    pass


class Student(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommitBase(BaseModel):
    project_id: int
    student_id: int
    commit_hash: str
    commit_message: Optional[str] = None
    commit_date: Optional[datetime] = None
    files_changed: Optional[int] = None
    lines_added: Optional[int] = None
    lines_deleted: Optional[int] = None


class CommitCreate(CommitBase):
    pass


class Commit(CommitBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class IssueBase(BaseModel):
    project_id: int
    student_id: int
    issue_number: int
    title: str
    body: Optional[str] = None
    state: str
    created_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class IssueCreate(IssueBase):
    pass


class Issue(IssueBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsData(BaseModel):
    total_projects: int
    total_students: int
    total_commits: int
    total_issues: int
    commits_by_student: List[dict]
    issues_by_student: List[dict]
    recent_activity: List[dict]


class ProjectStatusBase(BaseModel):
    project_id: int
    has_readme: bool
    readme_files: List[str] = []
    total_files: int
    code_files: int
    doc_files: int
    config_files: int
    project_size_kb: float
    main_language: Optional[str] = None
    commit_count: int
    contributors: int
    last_commit: Optional[str] = None
    current_branch: str = "main"
    has_package_json: bool = False
    has_requirements_txt: bool = False
    has_dockerfile: bool = False
    quality_score: int = 0


class ProjectStatusCreate(ProjectStatusBase):
    pass


class ProjectStatus(ProjectStatusBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project_name: Optional[str] = None
    github_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProjectStatusSummary(BaseModel):
    total_projects: int
    projects_with_readme: int
    readme_coverage: float
    avg_quality_score: float
    language_distribution: dict
    avg_project_size: float
    avg_commit_count: float
    avg_contributors: float
    projects_by_score: dict 