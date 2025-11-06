<template>
  <div class="container">
    <h1>🌍 Monitoraggio Qualità dell'Aria - Stazioni ZeroC</h1>
    <div v-if="loading" class="loading">⏳ Caricamento stazioni...</div>
    <div v-if="error" class="error">❌ {{ error }}</div>
    <div v-if="stations && stations.length > 0">
      <p class="subtitle">{{ stations.length }} stazioni disponibili</p>
      <div class="stations-grid">
        <div v-for="s in stations" :key="s.id" class="card">
          <h3>{{ s.name || s.id }}</h3>
          <p v-if="s.address" class="address">📍 {{ s.address }}</p>
          <p v-if="s.site" class="site">🏢 {{ s.site }}</p>
          <button @click="go(s.id)">Visualizza dati →</button>
        </div>
      </div>
    </div>
    <div v-else-if="!loading && !error">
      <p>Nessuna stazione disponibile.</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const config = useRuntimeConfig()

const stations = ref(null)
const loading = ref(false)
const error = ref(null)

async function fetchStations() {
  loading.value = true
  try {
    const res = await $fetch(`${config.public.backendUrl}/api/stations`)
    // se l'upstream restituisce oggetto con lista in "data" o simile, adatta qua
    if (Array.isArray(res)) {
      stations.value = res
    } else if (Array.isArray(res.stations)) {
      stations.value = res.stations
    } else if (res.data && Array.isArray(res.data)) {
      stations.value = res.data
    } else {
      // fallback: cerca la prima proprietà array
      const arr = Object.values(res).find(v => Array.isArray(v))
      stations.value = arr || []
    }
  } catch (e) {
    error.value = 'Impossibile ottenere la lista stazioni: ' + (e.message || e)
  } finally {
    loading.value = false
  }
}

fetchStations()

function go(id) {
  router.push(`/station/${id}`)
}
</script>

<style scoped>
.container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.subtitle { color: #666; margin: 8px 0 24px 0; }
.loading { padding: 20px; text-align: center; font-size: 18px; }
.stations-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap:16px; }
.card { 
  border:1px solid #e0e0e0; 
  padding:20px; 
  border-radius:8px; 
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}
.card h3 { margin: 0 0 12px 0; color: #1976d2; }
.card .address { font-size: 14px; color: #666; margin: 8px 0; }
.card .site { font-size: 13px; color: #888; margin: 8px 0; }
.card button { 
  margin-top: 12px; 
  padding: 10px 16px; 
  background: #2196f3; 
  color: white; 
  border: none; 
  border-radius: 4px; 
  cursor: pointer;
  width: 100%;
  font-weight: 500;
}
.card button:hover { background: #1976d2; }
.error { color: #d32f2f; padding: 16px; background: #ffebee; border-radius: 4px; border-left: 4px solid #d32f2f; }
h1 { color: #333; margin-bottom: 8px; }
</style>