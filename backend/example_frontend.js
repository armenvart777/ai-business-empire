/**
 * Пример фронтенд кода для вызова Agents API из веб-интерфейса.
 *
 * Используйте этот код в вашем React/Next.js/Vue приложении.
 */

// API Base URL
const API_BASE_URL = 'http://localhost:8000';  // В production: ваш реальный домен

// ============================================
// API Client Functions
// ============================================

/**
 * Запустить Trend Scanner
 */
async function scanTrends(options = {}) {
  const response = await fetch(`${API_BASE_URL}/api/agents/scan-trends`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      sources: options.sources || ['google_trends', 'reddit', 'product_hunt'],
      min_score: options.minScore || 60,
      limit: options.limit || 20
    })
  });

  const data = await response.json();
  return data.job_id;
}

/**
 * Запустить Business Generator
 */
async function generateBusinessIdeas(options = {}) {
  const response = await fetch(`${API_BASE_URL}/api/agents/generate-ideas`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ideas_per_trend: options.ideasPerTrend || 5,
      min_priority_score: options.minPriorityScore || 70
    })
  });

  const data = await response.json();
  return data.job_id;
}

/**
 * Создать MVP
 */
async function createMVP(businessId, options = {}) {
  const response = await fetch(`${API_BASE_URL}/api/agents/create-mvp`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      business_id: businessId,
      auto_deploy: options.autoDeploy !== false,
      auto_merge: options.autoMerge !== false
    })
  });

  const data = await response.json();
  return data.job_id;
}

/**
 * Создать маркетинговую кампанию
 */
async function createMarketing(businessId, deploymentUrl, options = {}) {
  const response = await fetch(`${API_BASE_URL}/api/agents/create-marketing`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      business_id: businessId,
      deployment_url: deploymentUrl,
      duration_weeks: options.durationWeeks || 4,
      channels: options.channels || ['blog', 'email', 'social'],
      budget: options.budget || 500
    })
  });

  const data = await response.json();
  return data.job_id;
}

/**
 * Создать sales систему
 */
async function createSales(businessId, deploymentUrl, options = {}) {
  const response = await fetch(`${API_BASE_URL}/api/agents/create-sales`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      business_id: businessId,
      deployment_url: deploymentUrl,
      target_mrr: options.targetMRR || 5000,
      channels: options.channels || ['email', 'demo', 'chat'],
      automation_level: options.automationLevel || 'high'
    })
  });

  const data = await response.json();
  return data.job_id;
}

/**
 * Запустить весь pipeline (все 5 агентов)
 */
async function runFullPipeline(options = {}) {
  const response = await fetch(`${API_BASE_URL}/api/agents/full-pipeline`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      trend_sources: options.trendSources || ['google_trends', 'reddit'],
      min_trend_score: options.minTrendScore || 70,
      ideas_per_trend: options.ideasPerTrend || 3,
      min_idea_score: options.minIdeaScore || 75,
      auto_deploy: options.autoDeploy !== false,
      marketing_budget: options.marketingBudget || 500,
      target_mrr: options.targetMRR || 5000
    })
  });

  const data = await response.json();
  return data.job_id;
}

/**
 * Получить статус job
 */
async function getJobStatus(jobId) {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`);

  if (!response.ok) {
    throw new Error('Job not found');
  }

  return await response.json();
}

/**
 * Получить список всех jobs
 */
async function listJobs(agentType = null, limit = 50) {
  const params = new URLSearchParams();
  if (agentType) params.append('agent_type', agentType);
  params.append('limit', limit);

  const response = await fetch(`${API_BASE_URL}/api/jobs?${params}`);
  return await response.json();
}

/**
 * Poll job status до завершения
 */
async function waitForJob(jobId, options = {}) {
  const maxWaitTime = options.maxWaitTime || 3600000; // 1 hour
  const pollInterval = options.pollInterval || 5000; // 5 seconds
  const startTime = Date.now();

  while (true) {
    // Check timeout
    if (Date.now() - startTime > maxWaitTime) {
      throw new Error('Job timeout');
    }

    // Get status
    const status = await getJobStatus(jobId);

    // Check if completed
    if (status.status === 'completed') {
      return status.result;
    }

    if (status.status === 'failed') {
      throw new Error(status.error || 'Job failed');
    }

    // Callback for progress updates
    if (options.onProgress) {
      options.onProgress(status);
    }

    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }
}

// ============================================
// React Component Examples
// ============================================

/**
 * Пример React компонента для запуска Trend Scanner
 */
function TrendScannerButton() {
  const [loading, setLoading] = React.useState(false);
  const [jobId, setJobId] = React.useState(null);
  const [result, setResult] = React.useState(null);

  const handleScan = async () => {
    setLoading(true);

    try {
      // Start job
      const jobId = await scanTrends({
        sources: ['google_trends', 'reddit'],
        minScore: 70,
        limit: 20
      });

      setJobId(jobId);

      // Wait for completion
      const result = await waitForJob(jobId, {
        onProgress: (status) => {
          console.log('Status:', status.status);
        }
      });

      setResult(result);
      alert(`Found ${result.trends_count} trends!`);

    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleScan} disabled={loading}>
        {loading ? 'Scanning...' : 'Scan Trends'}
      </button>

      {jobId && <p>Job ID: {jobId}</p>}

      {result && (
        <div>
          <h3>Found {result.trends_count} trends:</h3>
          <ul>
            {result.trends.map((trend, i) => (
              <li key={i}>
                {trend.topic} - Score: {trend.score}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

/**
 * Пример React компонента для запуска Full Pipeline
 */
function FullPipelineButton() {
  const [loading, setLoading] = React.useState(false);
  const [status, setStatus] = React.useState(null);
  const [result, setResult] = React.useState(null);

  const handleRun = async () => {
    setLoading(true);

    try {
      // Start pipeline
      const jobId = await runFullPipeline({
        trendSources: ['google_trends', 'reddit'],
        minTrendScore: 70,
        ideasPerTrend: 3,
        minIdeaScore: 75,
        autoDeploy: true,
        marketingBudget: 500,
        targetMRR: 5000
      });

      // Poll for status
      const result = await waitForJob(jobId, {
        maxWaitTime: 3600000, // 1 hour
        pollInterval: 10000, // 10 seconds
        onProgress: (status) => {
          setStatus(status);
          console.log('Pipeline status:', status.status);
        }
      });

      setResult(result);

      // Show success
      const businessName = result.ideas[0]?.name || 'Unknown';
      const deploymentUrl = result.mvp?.deployment?.url || '';

      alert(`✅ Pipeline complete!\n\nBusiness: ${businessName}\nURL: ${deploymentUrl}`);

    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handleRun} disabled={loading}>
        {loading ? 'Running Pipeline...' : 'Run Full Pipeline'}
      </button>

      {status && (
        <div>
          <p>Status: {status.status}</p>
          <p>Agent: {status.agent_type}</p>
        </div>
      )}

      {result && (
        <div>
          <h3>Pipeline Results:</h3>
          <ul>
            <li>Trends: {result.trends?.length || 0}</li>
            <li>Ideas: {result.ideas?.length || 0}</li>
            <li>MVP URL: {result.mvp?.deployment?.url || 'N/A'}</li>
            <li>Marketing Reach: {result.marketing?.estimated_reach || 0}</li>
            <li>Sales Customers Needed: {result.sales?.estimated_customers_needed || 0}</li>
          </ul>
        </div>
      )}
    </div>
  );
}

// ============================================
// Vue Component Examples
// ============================================

/**
 * Пример Vue компонента
 */
const TrendScannerComponent = {
  data() {
    return {
      loading: false,
      jobId: null,
      result: null
    }
  },
  methods: {
    async scanTrends() {
      this.loading = true;

      try {
        const jobId = await scanTrends({ minScore: 70 });
        this.jobId = jobId;

        const result = await waitForJob(jobId);
        this.result = result;

        alert(`Found ${result.trends_count} trends!`);

      } catch (error) {
        alert('Error: ' + error.message);
      } finally {
        this.loading = false;
      }
    }
  },
  template: `
    <div>
      <button @click="scanTrends" :disabled="loading">
        {{ loading ? 'Scanning...' : 'Scan Trends' }}
      </button>

      <p v-if="jobId">Job ID: {{ jobId }}</p>

      <div v-if="result">
        <h3>Found {{ result.trends_count }} trends:</h3>
        <ul>
          <li v-for="trend in result.trends" :key="trend.id">
            {{ trend.topic }} - Score: {{ trend.score }}
          </li>
        </ul>
      </div>
    </div>
  `
};

// ============================================
// Vanilla JavaScript Example
// ============================================

/**
 * Пример использования с обычным JavaScript (без фреймворка)
 */
document.getElementById('scan-button')?.addEventListener('click', async () => {
  const button = event.target;
  button.disabled = true;
  button.textContent = 'Scanning...';

  try {
    // Start scan
    const jobId = await scanTrends({ minScore: 70 });

    // Wait for result
    const result = await waitForJob(jobId, {
      onProgress: (status) => {
        button.textContent = `Status: ${status.status}`;
      }
    });

    // Display results
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
      <h3>Found ${result.trends_count} trends:</h3>
      <ul>
        ${result.trends.map(t => `<li>${t.topic} - Score: ${t.score}</li>`).join('')}
      </ul>
    `;

    button.textContent = 'Scan Complete!';

  } catch (error) {
    alert('Error: ' + error.message);
    button.textContent = 'Scan Trends';
  } finally {
    button.disabled = false;
  }
});

// ============================================
// Export для использования в других файлах
// ============================================

export {
  scanTrends,
  generateBusinessIdeas,
  createMVP,
  createMarketing,
  createSales,
  runFullPipeline,
  getJobStatus,
  listJobs,
  waitForJob
};
