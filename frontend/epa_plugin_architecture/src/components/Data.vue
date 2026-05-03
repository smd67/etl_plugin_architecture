<!--
This file is the vue component implementation for a generic screen that can be 
used for the ETL Plugin Architecture. It consists of a table to display
the results plus the abilitym to save the table as a CSV file.
 -->
<template>
  <div class="my-division">
      <div class="spinner" v-if="loading"></div>
  </div>
  <div class="outer-div">
    <v-container class="table-container">
      <v-row>
        <div :style="titleStyle">
          <img :width="iconWidth" :height="iconHeight" :alt="title" :src="iconUrl">
          {{ title }}
        </div>
      </v-row>  
    </v-container>
    <v-container class="table-container">
      <v-row style="width: 50%; height: 75%">
        <v-text-field
          v-model="dataInput"
          :label="inputLabel"
          variant="outlined"
          :color="inputColor"
          @keydown.enter="fetchData"
        ></v-text-field>
      </v-row>
      <v-row>
        <v-data-table
          v-if="isUpdated"
          :headers="dataHeaders"
          :items="dataTable"
          :search="dataSearch"
          class="elevation-1"
          :key="dataKey"
          :style="tableStyle"
          :sort-by="sortBy"
        >
          <template v-slot:item.url="{ item }">
            <a :href="item.url" target="_blank">{{ item.url_text }}</a>
          </template>
          <!-- If you still want the default pagination controls alongside the search -->
          <template v-slot:footer.prepend>
            <v-text-field
              v-model="dataSearch"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              density="compact"
              variant="outlined"
              bg-color="#f5f5f5"
              hide-details
              class="flex-grow-1 mr-4"
            ></v-text-field>
            <!-- Add a v-spacer if needed to align items correctly with default footer content -->
            <v-spacer></v-spacer>
          </template>
          <template v-slot:item.description="{ item }">
            <div class="pre-wrap-cell">
              {{ item.description }}
            </div>
          </template>
        </v-data-table>
      </v-row>
      <v-row v-if="isUpdated">
        <v-spacer></v-spacer>
        <div class="d-flex justify-center align-center" style="padding-top: 20px; gap: 16px;">
          <v-btn variant="outlined" :color="buttonColor" :style="buttonStyle" @click="exportToCSV">
            Export to CSV
          </v-btn>
        </div>
        <v-spacer></v-spacer>
      </v-row>
    </v-container>
    <ErrorDialog ref="errorDialog"></ErrorDialog>
  </div>
</template>

<script setup>
  // Imports
  import { ref, onMounted } from 'vue';
  import api from "../api";
  import Papa from 'papaparse'; // Import PapaParse
  import ErrorDialog from './ErrorDialog.vue';

  // Data
  const errorDialog = ref(null);
  const loading = ref(false);
  const dataInput = ref(null);
  const dataTable = ref([]);
  const dataSearch = ref('');
  const dataKey = ref(0);
  const isUpdated = ref(false);
  const title = ref(null);
  const iconUrl = ref(null);
  const iconWidth = ref(0);
  const iconHeight = ref(0);
  const inputLabel = ref(null);
  const inputColor = ref(null);
  const titleStyle = ref(null);
  const tableStyle = ref(null);
  const tableHeaderColor = ref('#F5F5DC'); 
  const tableOddColor = ref('#F5F5DC'); 
  const tableEvenColor = ref('#ffffff'); 
  const buttonColor = ref('green'); 
  const buttonStyle = ref('#F5F5DC');
  const sortBy = ref([]);
  const csvFileName = ref("data.csv"); 
  const keyName = ref(null);

  // Table headers
  const dataHeaders = ref([]);

  
  // Initialize data on mount of component
  onMounted(async () => {
    console.log('IN Data.onMounted');
    await fetchDataHeaders();
    await fetchProperties();
    await fetchIcon();
    console.log('OUT Data.onMounted');
  });


  // Export the generated table to a csv file and download it
  const exportToCSV = () => {
    // 1. Get your data source
    const jsonData = dataTable.value;

    // 2. Convert the JSON data to CSV format using PapaParse
    const csv = Papa.unparse(jsonData);

    // 3. Create a Blob and initiate the download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.setAttribute('href', url);
    link.setAttribute('download', csvFileName.value); // Set the download file name
    link.click();
  };

  // Retrieve Data from the database through a REST call.
  const fetchData = async () => {
    isUpdated.value = false;
    loading.value = true;
    dataTable.value = [];
    const config = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    const requestBody = {
      [keyName.value]: dataInput.value,
    };
    console.log("requestBody=" + JSON.stringify(requestBody));
    try {
        const response = await api.post('/fetch', requestBody, config);
        console.log("response=" + JSON.stringify(response));
        dataTable.value = response.data.data;
        isUpdated.value = true;
        loading.value = false;
    } catch (e) {
        loading.value = false;
        console.log("error=" + e)
        const result = await errorDialog.value.open(
          'Confirm Error',
          'Error fetching data. body=' + JSON.stringify(requestBody) + '; exception=' + e,
          { color: 'red lighten-3' }
        );
    }
  };

  // Retrieve headers from the database through a REST call.
  const fetchDataHeaders = async () => {
    const config = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    try {
        const response = await api.get('/get-table-headers', config);
        console.log("response=" + JSON.stringify(response));
        dataHeaders.value = response.data;
    } catch (e) {
        loading.value = false;
        console.log("error=" + e)
        const result = await errorDialog.value.open(
          'Confirm Error',
          'Error fetching data.' + '; exception=' + e,
          { color: 'red lighten-3' }
        );
    }
  };

  // Retrieve properties from the database through a REST call.
  const fetchProperties = async () => {
    const config = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    try {
        const response = await api.get('/get-properties', config);
        console.log("response=" + JSON.stringify(response));
        title.value = response.data.title;
        iconWidth.value = response.data.icon_width;
        iconHeight.value = response.data.icon_height;
        inputLabel.value = response.data.input_label;
        titleStyle.value = response.data.title_style;
        tableStyle.value = response.data.table_style;
        inputColor.value = response.data.input_color;
        tableHeaderColor.value = response.data.table_header_color; 
        tableOddColor.value = response.data.table_odd_color; 
        tableEvenColor.value = response.data.table_even_color;
        buttonColor.value = response.data.button_color; 
        buttonStyle.value = response.data.button_style;
        csvFileName.value = response.data.csv_file_name;
        sortBy.value = response.data.sort_by;
        keyName.value = response.data.key_name;
        console.log("keyName=" + keyName.value);
    } catch (e) {
        loading.value = false;
        console.log("error=" + e)
        const result = await errorDialog.value.open(
          'Confirm Error',
          'Error fetching data.' + '; exception=' + e,
          { color: 'red lighten-3' }
        );
    }
  };

  // Retrieve the icon imnage to display from the database through a REST call.
  const fetchIcon = async () => {
    const config = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    try {
        const response = await api.get('/get-icon', config);
        console.log("response=" + JSON.stringify(response));
        iconUrl.value = response.data;
    } catch (e) {
        loading.value = false;
        console.log("error=" + e)
        const result = await errorDialog.value.open(
          'Confirm Error',
          'Error fetching data.' + '; exception=' + e,
          { color: 'red lighten-3' }
        );
    }
  };
</script>

<style>
  .my-division {
    padding-top: 15px;
    padding-bottom: 15px;
    padding-left: 100px;
  }

  .spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-left-color: #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
  }
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  /* Set header background color */
  .theme--light.v-data-table > .v-data-table__wrapper > table > thead > tr > th {
    background: var(--v-primary-base); /* Use a CSS variable for theme color */
  }

  /* Set alternating row colors (striped table) */
  .v-table tbody tr:nth-child(odd) {
    background-color: v-bind(tableOddColor); /* Light grey for odd rows */
  }
  .v-table thead th {
    background-color:  v-bind(tableHeaderColor); /* White for odd rows */
  }
  .v-table tbody tr:nth-child(even) {
    background-color: v-bind(tableEvenColor); /* White for even rows */
  }
</style>
<style scoped>
  .table-container { 
    width: 80%;
  }

  .outer-div {
    width: 100%;
    padding-top: 30px;
  }

  .pre-wrap-cell {
    white-space: pre-wrap; /* or pre-line */
  }

   /* Specific styles for screens smaller than 600px */
  @media (max-width: 600px) {
    .table-container { 
      width: 100%
    }
    .outer-div {
      width: 100%;
    }
  }
</style>