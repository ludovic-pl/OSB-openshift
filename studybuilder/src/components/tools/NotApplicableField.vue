<template>
  <label v-if="label" class="v-label">{{ label }}</label>
  <v-row class="align-center">
    <v-col cols="10">
      <slot name="mainField" :not-applicable="notApplicable" />
    </v-col>
    <v-col cols="2">
      <v-checkbox
        v-model="notApplicable"
        color="primary"
        data-cy="not-applicable-checkbox"
        :label="naLabel"
        hide-details
        :disabled="disabled"
        @change="cleanFunction"
      />
    </v-col>
  </v-row>
</template>

<script setup>
import { ref, watch } from 'vue'
import { i18n } from '@/plugins/i18n'

const props = defineProps({
  label: {
    type: String,
    default: '',
  },
  hint: {
    type: String,
    default: '',
  },
  naLabel: {
    type: String,
    default: () => i18n.t('_global.not_applicable'),
  },
  cleanFunction: {
    type: Function,
    default: undefined,
  },
  checked: Boolean,
  disabled: {
    type: Boolean,
    default: false,
  },
})

const notApplicable = ref(false)

watch(
  () => props.checked,
  (value) => {
    notApplicable.value = value
  }
)

notApplicable.value = props.checked
</script>
