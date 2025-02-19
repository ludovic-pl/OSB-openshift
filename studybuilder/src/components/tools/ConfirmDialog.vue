<template>
  <v-dialog
    :model-value="dialog"
    :max-width="options.width"
    :style="{ zIndex: options.zIndex }"
    @keydown.esc="cancel"
  >
    <v-card
      :border="cardClasses"
      class="pa-1"
      style="border-radius: 20px"
    >
    <v-card-title v-if="options.title" class="dialogText">
      {{ options.title }}
    </v-card-title>
      <v-card-text v-if="message" class="pt-2 dialogText">
        <v-row no-gutters class="align-center pa-2">
          <v-col cols="12">
            <div class="text-body-1 mt-1" v-html="message" />
          </v-col>
        </v-row>
        <v-divider class="pa-2" />
        <v-row>
          <v-col class="text-center">
            <v-btn
              v-if="!options.noCancel"
              variant="outlined"
              data-cy="cancel-popup"
              class="mr-4"
              rounded="xl"
              @click="cancel"
            >
              {{ options.cancelLabel }}
            </v-btn>
            <slot name="actions">
              <v-btn
                v-if="options.redirect === null"
                :color="btnClasses"
                rounded="xl"
                data-cy="continue-popup"
                @click="agree"
              >
                {{ options.agreeLabel }}
              </v-btn>
              <v-btn
                v-else
                data-cy="continue-popup"
                variant="outlined"
                rounded="xl"
                @click="agreeAndRedirect"
              >
                {{ options.agreeLabel }}
              </v-btn>
            </slot>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      resolve: null,
      reject: null,
      message: null,
      type: null,
      options: {
        title: null,
        type: 'success',
        width: 450,
        zIndex: 3000,
        noCancel: false,
        agreeLabel: this.$t('_global.continue'),
        cancelLabel: this.$t('_global.cancel'),
        cancelIsPrimaryAction: false,
        redirect: null,
      },
    }
  },
  computed: {
    cardClasses() {
      return this.btnClasses + ' lg opacity-100'
    },  
    btnClasses() {
      if (this.options.type === 'warning') {
        return 'warning'
      } else if (this.options.type === 'info') {
        return 'info'
      } else {
        return 'success'
      }
    },
  },
  methods: {
    open(message, options) {
      this.dialog = true
      this.message = message
      this.options = Object.assign(this.options, options)
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    agree() {
      this.resolve(true)
      this.dialog = false
    },
    agreeAndRedirect() {
      this.dialog = false
      this.$router.push(this.options.redirect)
    },
    cancel() {
      this.resolve(false)
      this.dialog = false
    },
  },
}
</script>
<style>
.dialogText {
  color: rgb(var(--v-theme-nnTrueBlue));
}
</style>