<template>
  <div class="container">
    <button @click="$router.back()">← Torna alla lista</button>
    
    <div v-if="loading">Caricamento...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="payload">
      <h1>{{ payload.name || 'Stazione' }}</h1>
      <div class="info">
        <p v-if="payload.address"><strong>Indirizzo:</strong> {{ payload.address }}</p>
        <p v-if="payload.site"><strong>Sito:</strong> {{ payload.site }}</p>
      </div>

      <div class="header">
        <div class="metric-select">
          <label>Seleziona metrica:</label>
          <select v-model="selectedMetric">
            <option v-for="m in metrics" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <div class="badge">
          Media ponderata (ultimi 7 giorni): <strong>{{ formattedWeighted }}</strong>
        </div>
      </div>

      <div v-if="series && series.length">
        <h3>Ultimi 10 giorni</h3>
        <table class="table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Min</th>
              <th>Media</th>
              <th>Max</th>
              <th>Campioni</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(d, idx) in seriesDisplay" :key="idx">
              <td>{{ d.date || d.day || ('#' + idx) }}</td>
              <td>{{ formatValue(d.min) }}</td>
              <td>{{ formatValue(d.average) }}</td>
              <td>{{ formatValue(d.max) }}</td>
              <td>{{ d.sample_size ?? '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else>
        Nessun dato disponibile per la metrica selezionata.
      </div>
    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const id = route.params.id
const config = useRuntimeConfig()

const payload = ref(null)
const loading = ref(false)
const error = ref(null)
const selectedMetric = ref(null)

async function fetchDetail() {
  loading.value = true
  try {
    payload.value = await $fetch(`${config.public.backendUrl}/api/stations/${id}`)
    
    if (payload.value.metrics && Array.isArray(payload.value.metrics) && payload.value.metrics.length > 0) {
      selectedMetric.value = payload.value.metrics[0].name
    } else {
      selectedMetric.value = null
    }
  } catch (e) {
    error.value = 'Impossibile caricare dettaglio: ' + (e.message || e)
  } finally {
    loading.value = false
  }
}

fetchDetail()

const metrics = computed(() => {
  if (!payload.value || !payload.value.metrics) return []
  
  if (Array.isArray(payload.value.metrics)) {
    return payload.value.metrics.map(m => m.name)
  }
  return []
})

const series = computed(() => {
  if (!payload.value || !selectedMetric.value || !payload.value.metrics) return []
  // Trova la metrica selezionata nell'array metrics
  const metric = payload.value.metrics.find(m => m.name === selectedMetric.value)
  if (!metric || !metric.data_points) return []
  // data_points è l'array con {date, min, average, max, sample_size}
  return metric.data_points || []
})

// Ordina per data se presente (più recente primo), altrimenti lascia ordine ma mostro ultimi 10
const seriesDisplay = computed(() => {
  const s = series.value.slice()
  if (!s || s.length === 0) return []
  const key = s[0].date ? 'date' : (s[0].day ? 'day' : null)
  if (key) {
    try {
      s.sort((a,b) => (b[key] || "").localeCompare(a[key] || ""))
    } catch (e) {}
  } else {
    s.reverse() // mostra i più recenti per primi se assume ordine cronologico originale
  }
  return s.slice(0, 10)
})

const formattedWeighted = computed(() => {
  if (!payload.value || !payload.value.weighted_averages) return '-'
  const val = payload.value.weighted_averages[selectedMetric.value]
  return val == null ? 'N/A' : Number(val).toFixed(2)
})

function formatValue(val) {
  if (val == null) return '-'
  return Number(val).toFixed(2)
}
</script>

<style scoped>
.container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.info { margin: 16px 0; padding: 12px; background: #f5f5f5; border-radius: 6px; }
.header { display:flex; align-items:center; gap:20px; margin:20px 0; flex-wrap: wrap; }
.badge { background:#e8f5e9; padding:12px 16px; border-radius:6px; font-size: 14px; }
.metric-select { display: flex; align-items: center; gap: 8px; }
.metric-select select { padding: 8px 12px; border-radius: 4px; border: 1px solid #ddd; }
.table { width:100%; border-collapse:collapse; margin-top:12px; }
.table th, .table td { border:1px solid #e0e0e0; padding:10px; text-align:left; }
.table th { background: #f5f5f5; font-weight: 600; }
.table tbody tr:hover { background: #fafafa; }
.error { color: red; padding: 12px; background: #ffebee; border-radius: 4px; }
button { padding: 8px 16px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 16px; }
button:hover { background: #1976d2; }
h1 { margin: 16px 0; }
h3 { margin: 16px 0 8px 0; }
</style>