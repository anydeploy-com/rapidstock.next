<template>
  <div class="container">
    <div class="hero">
      <h1 class="hero-title">Welcome to RapidStock</h1>
      <p class="hero-subtitle">Your modern inventory management solution</p>
      <div class="hero-features">
        <div class="feature-card">
          <h3>📦 Inventory Management</h3>
          <p>Track and manage your products with ease</p>
        </div>
        <div class="feature-card">
          <h3>📊 Analytics</h3>
          <p>Get insights into your stock and sales</p>
        </div>
        <div class="feature-card">
          <h3>🚚 Order Tracking</h3>
          <p>Monitor orders from start to finish</p>
        </div>
      </div>
      <div class="cta">
        <NuxtLink to="/products" class="btn btn-primary">Browse Products</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
useHead({
  title: 'RapidStock - Modern Inventory Management',
  meta: [
    { name: 'description', content: 'RapidStock is a modern inventory management solution built with Nuxt 4' }
  ]
})
</script>

<style scoped>
.hero {
  text-align: center;
  padding: 4rem 0;
}

.hero-title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 3rem;
}

.hero-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.feature-card p {
  color: #666;
}

.cta {
  margin-top: 2rem;
}

.btn {
  display: inline-block;
  padding: 1rem 2rem;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-features {
    grid-template-columns: 1fr;
  }
}
</style>