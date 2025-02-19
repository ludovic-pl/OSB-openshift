<template>
  <v-dialog
    :model-value="open"
    :scrollable="scrollable"
    persistent
    :max-width="maxWidth"
    @keydown.esc="cancel"
  >
    <v-card data-cy="form-body" elevation="0" rounded="xl">
      <v-card-title class="d-flex align-center">
        <span class="dialog-title">{{ title }}</span>
        <HelpButtonWithPanels
          v-if="helpItems"
          :title="$t('_global.help')"
          :help-text="helpText"
          :items="helpItems"
        />
        <v-btn
          v-if="formUrl"
          color="secondary"
          class="ml-2"
          size="small"
          @click="copyUrl"
        >
          {{ $t('_global.copy_link') }}
        </v-btn>
      </v-card-title>
      <v-divider />
      <v-card-text>
        <slot name="body" />
      </v-card-text>
      <v-divider />
      <v-card-actions class="pr-6 my-2">
        <v-spacer />
        <div>
          <slot name="actions" />
        </div>
        <v-btn
          data-cy="cancel-button"
          :disabled="actionDisabled"
          variant="outlined"
          rounded
          elevation="0"
          width="120px"
          @click="cancel"
        >
          {{ $t('_global.cancel') }}
        </v-btn>
        <v-btn
          v-if="!noSaving"
          data-cy="save-button"
          color="secondary"
          variant="flat"
          width="120px"
          :loading="working"
          :disabled="actionDisabled"
          rounded
          @click="submit"
        >
          {{ actionButtonLabel }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <ConfirmDialog ref="confirm" :text-cols="6" :action-cols="5" />
</template>

<script>
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import HelpButtonWithPanels from '@/components/tools/HelpButtonWithPanels.vue'

export default {
  components: {
    ConfirmDialog,
    HelpButtonWithPanels,
  },
  props: {
    actionLabel: {
      type: String,
      default: null,
    },
    title: {
      type: String,
      default: '',
    },
    helpItems: {
      type: Array,
      default: null,
    },
    helpText: {
      type: String,
      required: false,
      default: '',
    },
    open: Boolean,
    maxWidth: {
      type: String,
      default: '800px',
    },
    noSaving: {
      type: Boolean,
      default: false,
    },
    formUrl: {
      type: String,
      default: '',
    },
    scrollable: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['close', 'submit'],
  data() {
    return {
      actionDisabled: false,
      working: false,
    }
  },
  computed: {
    actionButtonLabel() {
      return this.actionLabel ? this.actionLabel : this.$t('_global.save')
    },
  },
  watch: {
    open() {
      this.working = false
    },
  },
  methods: {
    copyUrl() {
      navigator.clipboard.writeText(this.formUrl)
    },
    cancel() {
      this.working = false
      this.$emit('close')
    },
    disableActions() {
      this.actionDisabled = true
    },
    enableActions() {
      this.actionDisabled = false
    },
    async confirm(message, options) {
      return await this.$refs.confirm.open(message, options)
    },
    async submit() {
      if (this.$parent.$refs?.observer) {
        const { valid } = await this.$parent.$refs.observer.validate()
        if (!valid) {
          return
        }
      }
      this.working = true
      this.$emit('submit')
    },
  },
}
</script>
