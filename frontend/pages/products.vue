<template>
  <div class="container">
    <h1>Products</h1>
    <p>Product management page - coming soon!</p>
    <div class="back-link">
      <NuxtLink to="/" class="btn btn-secondary">← Back to Home</NuxtLink>
    </div>
  </div>
</template>

<script setup>
useHead({
  title: 'Products - RapidStock',
})
</script>

<style scoped>
.back-link {
  margin-top: 2rem;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
  padding: 0.75rem 1.5rem;
  text-decoration: none;
  border-radius: 4px;
  display: inline-block;
}

.btn-secondary:hover {
  background-color: #5a6268;
}
</style>