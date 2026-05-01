<!--
This file is the vue component implementation an error dialog.
 -->
<template>
  <v-dialog v-model="dialog" :max-width="options.width" :style="{ zIndex: options.zIndex }">
    <v-card>
      <v-card-title class="headline" :class="options.color">
        {{ title }}
      </v-card-title>
      <v-card-text>
        {{ message }}
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="text"
          @click="agree"
        >
          OK
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue';

const dialog = ref(false);
const resolve = ref(null);
const reject = ref(null);
const message = ref('');
const title = ref('');
const options = reactive({
  color: 'primary',
  width: 400,
  zIndex: 2000,
});

/**
 * Open the dialog
 * @param {string} pTitle
 * @param {string} pMessage
 * @param {object} pOptions
 * @returns {Promise<boolean>}
 */
const open = (pTitle, pMessage, pOptions) => {
  title.value = pTitle;
  message.value = pMessage;
  Object.assign(options, pOptions);
  dialog.value = true;
  return new Promise((res, rej) => {
    resolve.value = res;
    reject.value = rej;
  });
};

const agree = () => {
  dialog.value = false;
  resolve.value(true);
};

// Expose the open function to the parent component via template refs
defineExpose({
  open,
});
</script>
