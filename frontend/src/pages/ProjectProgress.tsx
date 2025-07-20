import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Badge, ProgressBar, Alert, Button, Spinner, Form } from 'react-bootstrap';
import ReactECharts from 'echarts-for-react';

interface ProjectProgressSummary {
  total_projects: number;
  tracking_start_date: string;
  tracking_end_date: string;
  total_days: number;
  projects_with_activity: number;
  total_commits: number;
  total_issues_created: number;
  total_issues_closed: number;
  daily_activity_summary: Array<{
    date: string;
    projects_with_commits: number;
    total_commits: number;
    total_lines_added: number;
    total_issues_created: number;
    total_issues_closed: number;
  }>;
  project_activity_ranking: Array<{
    project_name: string;
    github_url: string;
    active_days: number;
    total_commits: number;
    total_lines_added: number;
    total_issues_created: number;
    total_issues_closed: number;
  }>;
}

interface CalendarData {
  date: string;
  projects_with_commits: number;
  total_commits: number;
  total_lines_added: number;
  total_issues_created: number;
  total_issues_closed: number;
  project_details: Array<{
    project_id: number;
    project_name: string;
    github_url: string;
    has_commit: boolean;
    commit_count: number;
    lines_added: number;
    issues_created: number;
    issues_closed: number;
  }>;
}

const ProjectProgress: React.FC = () => {
  const [summary, setSummary] = useState<ProjectProgressSummary | null>(null);
  const [calendarData, setCalendarData] = useState<CalendarData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState({
    start_date: '2025-07-09',
    end_date: '2025-08-13'
  });

  useEffect(() => {
    fetchData();
  }, [dateRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 获取摘要数据
      const summaryResponse = await fetch('/api/project-progress/summary');
      if (!summaryResponse.ok) {
        throw new Error('获取摘要数据失败');
      }
      const summaryData = await summaryResponse.json();
      setSummary(summaryData);

      // 获取日历数据
      const calendarResponse = await fetch(`/api/project-progress/calendar?start_date=${dateRange.start_date}&end_date=${dateRange.end_date}`);
      if (!calendarResponse.ok) {
        throw new Error('获取日历数据失败');
      }
      const calendarData = await calendarResponse.json();
      setCalendarData(calendarData);

    } catch (err) {
      setError(err instanceof Error ? err.message : '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      const response = await fetch('/api/project-progress/sync', {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('同步失败');
      }
      
      // 重新获取数据
      await fetchData();
      alert('项目进度数据同步完成！');
    } catch (err) {
      setError(err instanceof Error ? err.message : '同步失败');
    } finally {
      setSyncing(false);
    }
  };

  const getActivityColor = (commits: number) => {
    if (commits === 0) return 'light';
    if (commits <= 2) return 'success';
    if (commits <= 5) return 'warning';
    return 'danger';
  };

  const getCommitChartOption = () => ({
    title: {
      text: '每日提交统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['提交数', '活跃项目数'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: summary?.daily_activity_summary.map(item => item.date) || [],
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '提交数',
        position: 'left'
      },
      {
        type: 'value',
        name: '活跃项目数',
        position: 'right'
      }
    ],
    series: [
      {
        name: '提交数',
        type: 'bar',
        data: summary?.daily_activity_summary.map(item => item.total_commits) || [],
        itemStyle: {
          color: '#1890ff'
        }
      },
      {
        name: '活跃项目数',
        type: 'line',
        yAxisIndex: 1,
        data: summary?.daily_activity_summary.map(item => item.projects_with_commits) || [],
        itemStyle: {
          color: '#52c41a'
        }
      }
    ]
  });

  const getIssueChartOption = () => ({
    title: {
      text: '每日Issue活动',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['创建Issue', '关闭Issue'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: summary?.daily_activity_summary.map(item => item.date) || [],
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '创建Issue',
        type: 'bar',
        data: summary?.daily_activity_summary.map(item => item.total_issues_created) || [],
        itemStyle: {
          color: '#fa8c16'
        }
      },
      {
        name: '关闭Issue',
        type: 'bar',
        data: summary?.daily_activity_summary.map(item => item.total_issues_closed) || [],
        itemStyle: {
          color: '#f5222d'
        }
      }
    ]
  });

  const getProjectRankingChartOption = () => ({
    title: {
      text: '项目活跃度排名',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: summary?.project_activity_ranking.slice(0, 10).map(item => item.project_name) || [],
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        type: 'bar',
        data: summary?.project_activity_ranking.slice(0, 10).map(item => item.total_commits) || [],
        itemStyle: {
          color: '#722ed1'
        }
      }
    ]
  });

  const renderCalendar = () => {
    if (!calendarData.length) return null;

    const weeks = [];
    let currentWeek = [];
    let currentDate = new Date(dateRange.start_date);
    const endDate = new Date(dateRange.end_date);

    while (currentDate <= endDate) {
      const dateStr = currentDate.toISOString().split('T')[0];
      const dayData = calendarData.find(d => d.date === dateStr);
      
      currentWeek.push({
        date: dateStr,
        data: dayData
      });

      if (currentDate.getDay() === 6 || currentDate.getTime() === endDate.getTime()) {
        weeks.push([...currentWeek]);
        currentWeek = [];
      }

      currentDate.setDate(currentDate.getDate() + 1);
    }

    return (
      <div className="calendar-container">
        <h5 className="mb-3">项目活动日历</h5>
        <div className="calendar">
          {/* 星期标题 */}
          <div className="calendar-header">
            {['日', '一', '二', '三', '四', '五', '六'].map(day => (
              <div key={day} className="calendar-day-header">{day}</div>
            ))}
          </div>
          
          {/* 日历内容 */}
          {weeks.map((week, weekIndex) => (
            <div key={weekIndex} className="calendar-week">
              {week.map((day, dayIndex) => (
                <div 
                  key={dayIndex} 
                  className={`calendar-day ${day.data ? 'has-data' : ''} ${selectedDate === day.date ? 'selected' : ''}`}
                  onClick={() => setSelectedDate(day.date)}
                >
                  <div className="calendar-date">{new Date(day.date).getDate()}</div>
                  {day.data && (
                    <div className="calendar-data">
                      <div className="commit-indicator">
                        {day.data.projects_with_commits > 0 && (
                          <Badge bg={getActivityColor(day.data.total_commits)}>
                            {day.data.total_commits}
                          </Badge>
                        )}
                      </div>
                      <div className="issue-indicator">
                        {day.data.total_issues_created > 0 && (
                          <small className="text-warning">+{day.data.total_issues_created}</small>
                        )}
                        {day.data.total_issues_closed > 0 && (
                          <small className="text-success">-{day.data.total_issues_closed}</small>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderSelectedDateDetails = () => {
    if (!selectedDate) return null;

    const dayData = calendarData.find(d => d.date === selectedDate);
    if (!dayData) return null;

    return (
      <Card className="mt-3">
        <Card.Header>
          <h6 className="mb-0">{selectedDate} 项目活动详情</h6>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={3}>
              <div className="text-center">
                <h4>{dayData.total_commits}</h4>
                <small>总提交数</small>
              </div>
            </Col>
            <Col md={3}>
              <div className="text-center">
                <h4>{dayData.projects_with_commits}</h4>
                <small>活跃项目数</small>
              </div>
            </Col>
            <Col md={3}>
              <div className="text-center">
                <h4>{dayData.total_issues_created}</h4>
                <small>创建Issue</small>
              </div>
            </Col>
            <Col md={3}>
              <div className="text-center">
                <h4>{dayData.total_issues_closed}</h4>
                <small>关闭Issue</small>
              </div>
            </Col>
          </Row>
          
          {dayData.project_details.length > 0 && (
            <div className="mt-3">
              <h6>项目详情:</h6>
              <Table size="sm">
                <thead>
                  <tr>
                    <th>项目名称</th>
                    <th>提交数</th>
                    <th>代码行数</th>
                    <th>Issue活动</th>
                  </tr>
                </thead>
                <tbody>
                  {dayData.project_details.map((project, index) => (
                    <tr key={index}>
                      <td>
                        <a href={project.github_url} target="_blank" rel="noopener noreferrer">
                          {project.project_name}
                        </a>
                      </td>
                      <td>
                        {project.has_commit ? (
                          <Badge bg={getActivityColor(project.commit_count)}>
                            {project.commit_count}
                          </Badge>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>{project.lines_added > 0 ? `+${project.lines_added}` : '-'}</td>
                      <td>
                        {project.issues_created > 0 && (
                          <Badge bg="warning" className="me-1">+{project.issues_created}</Badge>
                        )}
                        {project.issues_closed > 0 && (
                          <Badge bg="success">-{project.issues_closed}</Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          )}
        </Card.Body>
      </Card>
    );
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
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>项目进度跟踪</h2>
        <Button 
          variant="primary" 
          onClick={handleSync} 
          disabled={syncing}
        >
          {syncing ? <Spinner animation="border" size="sm" /> : '同步数据'}
        </Button>
      </div>

      {summary && (
        <>
          {/* 统计卡片 */}
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
                  <h4>{summary.projects_with_activity}</h4>
                  <Card.Text>活跃项目数</Card.Text>
                  <ProgressBar 
                    now={(summary.projects_with_activity / summary.total_projects) * 100} 
                    variant="success" 
                    className="mt-2"
                  />
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h4>{summary.total_commits}</h4>
                  <Card.Text>总提交数</Card.Text>
                </Card.Body>
              </Card>
            </Col>
            <Col md={3}>
              <Card className="text-center">
                <Card.Body>
                  <h4>{summary.total_issues_created}</h4>
                  <Card.Text>总Issue数</Card.Text>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {/* 图表 */}
          <Row className="mb-4">
            <Col md={6}>
              <Card>
                <Card.Body>
                  <ReactECharts option={getCommitChartOption()} style={{ height: '400px' }} />
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Body>
                  <ReactECharts option={getIssueChartOption()} style={{ height: '400px' }} />
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Row className="mb-4">
            <Col md={12}>
              <Card>
                <Card.Body>
                  <ReactECharts option={getProjectRankingChartOption()} style={{ height: '400px' }} />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </>
      )}

      {/* 日历视图 */}
      <Row className="mb-4">
        <Col md={12}>
          <Card>
            <Card.Body>
              {renderCalendar()}
              {renderSelectedDateDetails()}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* 项目排名表格 */}
      {summary && (
        <Row>
          <Col md={12}>
            <Card>
              <Card.Header>
                <h5 className="mb-0">项目活跃度排名</h5>
              </Card.Header>
              <Card.Body>
                <Table responsive striped hover>
                  <thead>
                    <tr>
                      <th>排名</th>
                      <th>项目名称</th>
                      <th>活跃天数</th>
                      <th>总提交数</th>
                      <th>代码行数</th>
                      <th>Issue活动</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.project_activity_ranking.map((project, index) => (
                      <tr key={index}>
                        <td>
                          <Badge bg={index < 3 ? 'primary' : 'secondary'}>
                            {index + 1}
                          </Badge>
                        </td>
                        <td>
                          <a href={project.github_url} target="_blank" rel="noopener noreferrer">
                            {project.project_name}
                          </a>
                        </td>
                        <td>
                          <ProgressBar 
                            now={(project.active_days / summary.total_days) * 100} 
                            label={`${project.active_days}天`}
                            variant="info"
                          />
                        </td>
                        <td>
                          <Badge bg={getActivityColor(project.total_commits)}>
                            {project.total_commits}
                          </Badge>
                        </td>
                        <td>{project.total_lines_added}</td>
                        <td>
                          {project.total_issues_created > 0 && (
                            <Badge bg="warning" className="me-1">+{project.total_issues_created}</Badge>
                          )}
                          {project.total_issues_closed > 0 && (
                            <Badge bg="success">-{project.total_issues_closed}</Badge>
                          )}
                        </td>
                        <td>
                          <Button 
                            variant="outline-primary" 
                            size="sm"
                            href={project.github_url}
                            target="_blank"
                          >
                            查看
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default ProjectProgress; 