<template>
  <v-app>
    <v-main>
      <Data />
    </v-main>
    <v-btn
      class="ma-2"
      icon="mdi-theme-light-dark"
      location="top right"
      position="absolute"
      @click="$vuetify.theme.cycle()"
    />
  </v-app>
</template>

<script setup>
  import Data from '@/components/Data.vue'
</script>
