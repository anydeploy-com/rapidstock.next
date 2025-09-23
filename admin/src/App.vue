<template>
  <div id="app">
    <header>
      <h1>{{ title }}</h1>
    </header>
    <main>
      <div class="welcome">
        <h2>Welcome to RapidStock Admin Panel</h2>
        <p>This is a Vue.js 3 application for managing your RapidStock inventory.</p>
        <div class="stats">
          <div class="stat-card">
            <h3>{{ stats.products }}</h3>
            <p>Products</p>
          </div>
          <div class="stat-card">
            <h3>{{ stats.orders }}</h3>
            <p>Orders</p>
          </div>
          <div class="stat-card">
            <h3>{{ stats.users }}</h3>
            <p>Users</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      title: 'RapidStock Admin',
      stats: {
        products: 125,
        orders: 43,
        users: 28
      }
    }
  }
}
</script>

<style>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f5f5f5;
  min-height: 100vh;
}

header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header h1 {
  margin: 0;
  font-size: 1.8rem;
}

main {
  padding: 2rem;
}

.welcome {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
}

.welcome h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.stats {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.stat-card {
  background: #3498db;
  color: white;
  padding: 1.5rem;
  border-radius: 6px;
  text-align: center;
  flex: 1;
}

.stat-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: bold;
}

.stat-card p {
  margin: 0;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .stats {
    flex-direction: column;
  }
  
  main {
    padding: 1rem;
  }
}
</style>