<script setup lang="ts">
import { ref, computed } from 'vue';
import axios from 'axios';
import { ParquetResponse} from '../types/parquet';

const data = ref<ParquetResponse | null>(null);
const selectedColumns = ref<string[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const totalRecords = ref(0);
const totalPages = computed(() => Math.ceil(totalRecords.value / pageSize.value));
const loading = ref(false);
const error = ref<string | null>(null);
const apiUrl = 'http://localhost:8000/api/parquet'
const apiLengthUrl = 'http://localhost:8000/api/parquet_length'
const selectedFilePath = ref<string>('');
const inputFilePath = ref<string>('');


const fetchParquetData = async (filePath: string) => {
  loading.value = true;
  error.value = null;

  try {
    const response = await axios.get(apiUrl, {
      params: {
        file_path: filePath,
        page: currentPage.value,
        page_size: pageSize.value,
      },
    });
    data.value = response.data as ParquetResponse;
    if (data.value) {
      if (selectedColumns.value.length == 0) {
          selectedColumns.value = Object.keys(data.value.schema_value);
      }
    }
    

  } catch (e : any) {
     if (e.response) {
         error.value = `Error fetching data: ${e.response.status} - ${e.response.data.detail}`;
     } else {
         error.value = `An error occured: ${e.message}`
     }
  } finally {
    loading.value = false;
  }
};

const fetchTotalRecords = async (filePath: string) => {
    loading.value = true;
    error.value = null;
    try {
        const response = await axios.get(apiLengthUrl, {
            params: {
                file_path: filePath,
            },
        });
        totalRecords.value = response.data;
    } catch (e : any) {
        if (e.response) {
            error.value = `Error fetching data: ${e.response.status} - ${e.response.data.detail}`;
        } else {
            error.value = `An error occured: ${e.message}`
        }
    } finally {
        loading.value = false;
    }
}

const fetchAndSetData = async () => {
    selectedFilePath.value = inputFilePath.value;
    await fetchTotalRecords(inputFilePath.value);
    await fetchParquetData(selectedFilePath.value);
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchParquetData(selectedFilePath.value);
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchParquetData(selectedFilePath.value);
  }
};

const onPageSizeChange = (event: Event) => {
    const target = event.target as HTMLSelectElement;
    pageSize.value = Number(target.value);
    currentPage.value = 1; // reset to the first page when changing page size.
    fetchParquetData(selectedFilePath.value);
};

</script>

<template>
    <header class="header">
       <div class="file-selector">
            <label for="filePath">Parquet File:</label>
            <input type="text" id="filePath" v-model="inputFilePath" placeholder="Enter parquet filename..." />
             <button @click="fetchAndSetData" class="fetch-button">Fetch Data</button>
        </div>
    <h2 v-if="selectedFilePath && !error && !loading" class="file-title">
        Showing data for: {{ selectedFilePath }}
    </h2>
    </header>
    
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="loading" class="loading-message">Loading data...</div>

    <div v-if="data" class="data-container">
      <div class="column-selection">
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th v-for="column in selectedColumns" :key="column">{{ column }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in data.data" :key="idx">
              <td v-for="column in selectedColumns" :key="idx">
                  <template v-if="data.schema_value[column] === 'timestamp'">
                      {{ new Date(row[column] as Date).toLocaleString() }}
                  </template>
                  <template v-else>
                      {{ row[column] }}
                  </template>
              </td>
          </tr>
        </tbody>
      </table>
        
    <div class="pagination">
            <button :disabled="currentPage <= 1" @click="prevPage">Previous</button>
            <span> Page {{ currentPage }} of {{ totalPages }}</span>
            <button :disabled="currentPage >= totalPages" @click="nextPage">Next</button>
        </div>
    <div class="page-size">
          <label for="pageSizeSelect">Page Size:</label>
          <select id="pageSizeSelect" @change="onPageSizeChange" :value="pageSize">
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
          </select>
        </div>
    </div>
</template>

<style scoped>

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 10px;
}

.file-selector{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.file-title {
  margin-bottom: 10px;
}

.error-message {
  color: red;
  margin-bottom: 10px;
}

.loading-message {
    margin-bottom: 10px;
}

.column-selection {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.data-container {
  margin-top: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.data-table th,
.data-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
  height: 20px;
}


.pagination {
    margin-top: 10px;
    display: flex;
    gap: 10px;
    align-items: center;
}

.page-size {
        margin-top: 10px;
        display: flex;
        gap: 10px;
    }
</style>