import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Badge, ProgressBar, Button, Alert, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';

interface ProjectStatus {
  id: number;
  project_id: number;
  project_name: string;
  github_url: string;
  has_readme: boolean;
  readme_files: string[];
  total_files: number;
  code_files: number;
  doc_files: number;
  config_files: number;
  project_size_kb: number;
  main_language: string;
  commit_count: number;
  contributors: number;
  last_commit: string;
  current_branch: string;
  has_package_json: boolean;
  has_requirements_txt: boolean;
  has_dockerfile: boolean;
  quality_score: number;
  created_at: string;
  updated_at: string;
}

interface ProjectStatusSummary {
  total_projects: number;
  projects_with_readme: number;
  readme_coverage: number;
  avg_quality_score: number;
  language_distribution: Record<string, number>;
  avg_project_size: number;
  avg_commit_count: number;
  avg_contributors: number;
  projects_by_score: Record<string, number>;
}

const ProjectStatus: React.FC = () => {
  const [projectStatuses, setProjectStatuses] = useState<ProjectStatus[]>([]);
  const [summary, setSummary] = useState<ProjectStatusSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const fetchProjectStatuses = async () => {
    try {
      setLoading(true);
      const [statusesResponse, summaryResponse] = await Promise.all([
        fetch('/api/project-status/'),
        fetch('/api/project-status/summary/overview')
      ]);

      if (statusesResponse.ok && summaryResponse.ok) {
        const statuses = await statusesResponse.json();
        const summaryData = await summaryResponse.json();
        
        // 调试信息
        console.log('项目状态数据:', statuses);
        if (statuses.length > 0) {
          console.log('第一个项目的github_url:', statuses[0].github_url);
        }
        
        setProjectStatuses(statuses);
        setSummary(summaryData);
      } else {
        setError('获取项目状态失败');
      }
    } catch (err) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  };

  const triggerAnalysis = async () => {
    try {
      setAnalyzing(true);
      const response = await fetch('/api/project-status/analyze', {
        method: 'POST'
      });
      
      if (response.ok) {
        await fetchProjectStatuses();
        alert('项目分析完成！');
      } else {
        alert('项目分析失败');
      }
    } catch (err) {
      alert('分析过程中出现错误');
    } finally {
      setAnalyzing(false);
    }
  };

  const updateRepos = async () => {
    try {
      const response = await fetch('/api/project-status/update-repos', {
        method: 'POST'
      });
      
      if (response.ok) {
        alert('本地仓库更新成功！');
      } else {
        alert('本地仓库更新失败');
      }
    } catch (err) {
      alert('更新过程中出现错误');
    }
  };

  useEffect(() => {
    fetchProjectStatuses();
  }, []);

  const getQualityColor = (score: number) => {
    if (score >= 75) return 'success';
    if (score >= 50) return 'warning';
    return 'danger';
  };

  const getLanguageColor = (language: string) => {
    const colors: Record<string, string> = {
      'Python': 'primary',
      'JavaScript': 'warning',
      'TypeScript': 'info',
      'Java': 'danger',
      'C/C++': 'secondary',
      'Web': 'success'
    };
    return colors[language] || 'light';
  };

  if (loading) {
    return (
      <div className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">加载中...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>📊 项目状态总览</h2>
        <div>
          <Button 
            variant="outline-primary" 
            onClick={updateRepos} 
            className="me-2"
          >
            🔄 更新仓库
          </Button>
          <Button 
            variant="primary" 
            onClick={triggerAnalysis}
            disabled={analyzing}
          >
            {analyzing ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                分析中...
              </>
            ) : (
              '🔍 分析项目'
            )}
          </Button>
        </div>
      </div>

      {/* 统计摘要 */}
      {summary && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h4>{summary.total_projects}</h4>
                <Card.Text>总项目数</Card.Text>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h4>{summary.readme_coverage}%</h4>
                <Card.Text>README覆盖率</Card.Text>
                <ProgressBar 
                  now={summary.readme_coverage} 
                  variant="success" 
                  className="mt-2"
                />
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h4>{summary.avg_quality_score}/100</h4>
                <Card.Text>平均质量评分</Card.Text>
                <ProgressBar 
                  now={summary.avg_quality_score} 
                  variant="info" 
                  className="mt-2"
                />
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <h4>{summary.avg_commit_count}</h4>
                <Card.Text>平均提交次数</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* 编程语言分布 */}
      {summary && summary.language_distribution && (
        <Card className="mb-4">
          <Card.Header>
            <h5>💻 编程语言分布</h5>
          </Card.Header>
          <Card.Body>
            <Row>
              {Object.entries(summary.language_distribution).map(([lang, count]) => (
                <Col key={lang} md={2} className="mb-2">
                  <Badge 
                    bg={getLanguageColor(lang)} 
                    className="p-2 w-100"
                  >
                    {lang}: {count}
                  </Badge>
                </Col>
              ))}
            </Row>
          </Card.Body>
        </Card>
      )}

      {/* 项目列表 */}
      <Card>
        <Card.Header>
          <h5>📋 项目详细状态</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            {projectStatuses.map((status) => (
              <Col key={status.id} lg={6} xl={4} className="mb-3">
                <Card className="h-100 project-status-card">
                  <Card.Header className="d-flex justify-content-between align-items-center">
                    <div className="d-flex align-items-center">
                      {status.github_url ? (
                        <a 
                          href={status.github_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="project-name-link"
                          title="在GitHub中查看项目"
                        >
                          <h6 className="mb-0 me-2">{status.project_name}</h6>
                        </a>
                      ) : (
                        <h6 className="mb-0 me-2">{status.project_name}</h6>
                      )}
                      {status.github_url && (
                        <a 
                          href={status.github_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="btn btn-sm btn-outline-secondary github-button"
                          title="在GitHub中查看项目"
                        >
                          🔗
                        </a>
                      )}
                    </div>
                    <Badge bg={getQualityColor(status.quality_score)}>
                      {status.quality_score}/100
                    </Badge>
                  </Card.Header>
                  <Card.Body>
                    <div className="mb-2">
                      <strong>语言:</strong>{' '}
                      <Badge bg={getLanguageColor(status.main_language || '未知')}>
                        {status.main_language || '未知'}
                      </Badge>
                    </div>
                    
                    <div className="mb-2">
                      <strong>README:</strong>{' '}
                      {status.has_readme ? (
                        <Badge bg="success">✅ 已建立</Badge>
                      ) : (
                        <Badge bg="danger">❌ 未建立</Badge>
                      )}
                    </div>
                    
                    <div className="mb-2">
                      <strong>文件统计:</strong>
                      <div className="small text-muted">
                        总文件: {status.total_files} | 
                        代码: {status.code_files} | 
                        文档: {status.doc_files}
                      </div>
                    </div>
                    
                    <div className="mb-2">
                      <strong>开发活跃度:</strong>
                      <div className="small text-muted">
                        提交: {status.commit_count} | 
                        贡献者: {status.contributors}
                      </div>
                    </div>
                    
                    <div className="mb-2">
                      <strong>项目大小:</strong> {status.project_size_kb.toFixed(1)} KB
                    </div>
                    
                    {status.github_url && (
                      <div className="mb-2">
                        <strong>GitHub地址:</strong>
                        <div className="small">
                          <a 
                            href={status.github_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="github-link"
                            title="在GitHub中查看项目"
                          >
                            {status.github_url}
                          </a>
                        </div>
                      </div>
                    )}
                    
                    <div className="mb-2">
                      <strong>配置:</strong>
                      <div className="small">
                        {status.has_package_json && <Badge bg="primary" className="me-1">package.json</Badge>}
                        {status.has_requirements_txt && <Badge bg="info" className="me-1">requirements.txt</Badge>}
                        {status.has_dockerfile && <Badge bg="secondary" className="me-1">Docker</Badge>}
                      </div>
                    </div>
                    
                    <div className="text-muted small">
                      最后更新: {new Date(status.updated_at).toLocaleString()}
                    </div>
                  </Card.Body>
                  <Card.Footer>
                    <div className="d-flex justify-content-between align-items-center">
                      <small className="text-muted">
                        分支: {status.current_branch}
                      </small>
                      <div>
                        {status.github_url && (
                          <a 
                            href={status.github_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="btn btn-sm btn-outline-success me-2 github-button"
                            title="在GitHub中查看项目"
                          >
                            📂 GitHub
                          </a>
                        )}
                        <Link 
                          to={`/projects/${status.project_id}`} 
                          className="btn btn-sm btn-outline-primary"
                        >
                          查看详情
                        </Link>
                      </div>
                    </div>
                  </Card.Footer>
                </Card>
              </Col>
            ))}
          </Row>
        </Card.Body>
      </Card>
    </div>
  );
};

export default ProjectStatus; 