<template>
  <div class="bg-surface-container-lowest p-6 rounded-lg border border-outline-variant/10 h-80">
    <div class="mb-4">
      <h4 class="text-[10px] font-bold text-outline uppercase tracking-widest mb-1">Timeline Phân Tích</h4>
      <p class="text-xs text-secondary">Biểu đồ mật độ {{ verdict === 'FAKE' ? 'giả mạo' : 'thật' }} theo thời gian</p>
    </div>
    
    <div class="h-64 relative">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import Chart from 'chart.js/auto'

export default {
  name: 'TimelineChart',
  props: {
    timelineData: {
      type: Array,
      default: () => []
    },
    verdict: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const chartCanvas = ref(null)
    let chartInstance = null

    const initChart = () => {
      if (!chartCanvas.value) return

      const ctx = chartCanvas.value.getContext('2d')
      
      // Prepare data
      const labels = props.timelineData.map(d => d.frame)
      const densityData = props.timelineData.map(d => d.fake_density)

      // Determine color based on verdict
      const barColor = props.verdict === 'FAKE' ? '#F44336' : '#00897B'
      const backgroundColor = props.verdict === 'FAKE' ? 'rgba(244, 67, 54, 0.1)' : 'rgba(0, 137, 123, 0.1)'

      // Destroy existing chart if it exists
      if (chartInstance) {
        chartInstance.destroy()
      }

      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Fake Density (%)',
              data: densityData,
              borderColor: barColor,
              backgroundColor: backgroundColor,
              borderWidth: 2,
              fill: true,
              tension: 0.4,
              pointRadius: 0,
              pointHoverRadius: 6,
              pointBackgroundColor: barColor,
              pointBorderColor: '#fff',
              pointBorderWidth: 2
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            intersect: false,
            mode: 'index'
          },
          plugins: {
            legend: {
              display: true,
              labels: {
                color: 'rgba(255, 255, 255, 0.7)',
                font: {
                  size: 12
                },
                usePointStyle: true,
                padding: 15
              }
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: barColor,
              borderWidth: 1,
              padding: 12,
              displayColors: true,
              callbacks: {
                label: function(context) {
                  return `Fake Density: ${context.parsed.y.toFixed(1)}%`
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                color: 'rgba(255, 255, 255, 0.5)',
                font: {
                  size: 11
                },
                callback: function(value) {
                  return value + '%'
                }
              },
              grid: {
                color: 'rgba(255, 255, 255, 0.1)',
                drawBorder: false
              }
            },
            x: {
              ticks: {
                color: 'rgba(255, 255, 255, 0.5)',
                font: {
                  size: 11
                },
                maxTicksLimit: 10
              },
              grid: {
                display: false,
                drawBorder: false
              }
            }
          }
        }
      })
    }

    onMounted(() => {
      if (props.timelineData.length > 0) {
        initChart()
      }
    })

    watch(
      () => props.timelineData,
      () => {
        if (props.timelineData.length > 0) {
          initChart()
        }
      },
      { deep: true }
    )

    watch(
      () => props.verdict,
      () => {
        if (props.timelineData.length > 0) {
          initChart()
        }
      }
    )

    return {
      chartCanvas
    }
  }
}
</script>
