import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Table } from 'react-bootstrap'
import ReactECharts from 'echarts-for-react'
import axios from 'axios'

interface DashboardData {
  total_projects: number
  total_students: number
  total_commits: number
  total_issues: number
  commits_by_student: Array<{
    name: string
    github_username: string
    commit_count: number
  }>
  issues_by_student: Array<{
    name: string
    github_username: string
    issue_count: number
  }>
  recent_activity: Array<{
    type: string
    title: string
    student_name: string
    date: string
  }>
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/analytics/dashboard')
        setData(response.data)
      } catch (error) {
        console.error('获取仪表板数据失败:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const getCommitChartOption = () => ({
    title: {
      text: '学生提交统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: data?.commits_by_student.map(item => ({
          name: item.name,
          value: item.commit_count
        })) || [],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  })

  const getIssueChartOption = () => ({
    title: {
      text: '学生Issue统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: data?.issues_by_student.map(item => item.name) || []
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: data?.issues_by_student.map(item => item.issue_count) || [],
        type: 'bar'
      }
    ]
  })

  if (loading) {
    return <div>加载中...</div>
  }

  if (!data) {
    return <div>加载失败</div>
  }

  return (
    <div>
      <h2 className="mb-4">仪表板</h2>
      
      {/* 统计卡片 */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stat-card text-center">
            <Card.Body>
              <h3>{data.total_projects}</h3>
              <p>总项目数</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card text-center">
            <Card.Body>
              <h3>{data.total_students}</h3>
              <p>总学生数</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card text-center">
            <Card.Body>
              <h3>{data.total_commits}</h3>
              <p>总提交数</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card text-center">
            <Card.Body>
              <h3>{data.total_issues}</h3>
              <p>总Issue数</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* 图表 */}
      <Row className="mb-4">
        <Col md={6}>
          <div className="chart-container">
            <ReactECharts option={getCommitChartOption()} />
          </div>
        </Col>
        <Col md={6}>
          <div className="chart-container">
            <ReactECharts option={getIssueChartOption()} />
          </div>
        </Col>
      </Row>

      {/* 最近活动 */}
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5>最近活动</h5>
            </Card.Header>
            <Card.Body>
              <Table responsive>
                <thead>
                  <tr>
                    <th>类型</th>
                    <th>标题</th>
                    <th>学生</th>
                    <th>时间</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_activity.map((activity, index) => (
                    <tr key={index}>
                      <td>
                        <span className={`badge ${activity.type === 'commit' ? 'bg-success' : 'bg-primary'}`}>
                          {activity.type === 'commit' ? '提交' : 'Issue'}
                        </span>
                      </td>
                      <td>{activity.title}</td>
                      <td>{activity.student_name}</td>
                      <td>{new Date(activity.date).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard 