<template>
  <v-app-bar color="primary" elevation="2" height="70">
    <v-app-bar-nav-icon
      v-if="!props.hideAppBarNavIcon"
      data-cy="topbar-menu-button"
      elevation="6"
      @click="appStore.drawer = !appStore.drawer"
    />
    <div data-cy="topbar-logo" class="d-flex action" @click="navigateToRoot">
      <v-img
        class="mx-6"
        :src="sbLogoUrl"
        contain
        transition="scale-transition"
        width="190"
      />
      <div
        v-if="appEnv"
        class="mr-6 font-weight-black"
        style="font-size: xx-large"
      >
        {{ appEnv }}
      </div>
    </div>

    <v-toolbar-items class="hidden-xs-only">
      <v-btn
        v-for="app in availableApps"
        :key="app.name"
        :data-cy="app.name"
        class="text-capitalize"
        :to="{ name: app.name }"
        variant="text"
      >
        <v-icon class="mr-1" :icon="app.icon" />
        {{ app.name }}
      </v-btn>
      <v-btn
        v-if="isAuthenticated"
        class="text-capitalize"
        href="/neodash/"
        target="_blank"
        variant="text"
      >
        <v-icon icon="mdi-file-chart-outline" />
        {{ $t('_global.reports') }}
        <template #append>
          <v-icon icon="mdi-open-in-new" />
        </template>
      </v-btn>
    </v-toolbar-items>
    <v-spacer />
    <div v-if="isAuthenticated">
      <v-btn
        class="text-capitalize"
        data-cy="topbar-select-study"
        variant="text"
        @click="openSelectStudyDialog"
      >
        {{ $t('Topbar.select_study') }}
      </v-btn>
      <v-chip
        v-if="selectedStudy"
        data-cy="topbar-selected-study"
        class="ma-2"
        :color="
          currentStudyStatus === 'DRAFT'
            ? 'green'
            : currentStudyStatus === 'LOCKED'
              ? 'red'
              : 'blue'
        "
        variant="flat"
      >
        {{
          selectedStudy.current_metadata.identification_metadata.study_id ||
          selectedStudy.current_metadata.identification_metadata.study_acronym
        }}
        <v-icon
          v-if="currentStudyStatus === 'DRAFT'"
          location="right"
          size="small"
          icon="mdi-lock-open-outline"
        />
        <v-icon v-else location="right" size="small" icon="mdi-lock-outline" />
      </v-chip>
      <v-chip
        v-if="selectedStudy && selectedStudyVersion"
        :color="
          currentStudyStatus === 'DRAFT'
            ? 'green'
            : currentStudyStatus === 'LOCKED'
              ? 'red'
              : 'blue'
        "
        variant="flat"
      >
        v{{ selectedStudy && selectedStudyVersion }}
      </v-chip>
    </div>
    <v-btn
      data-cy="topbar-admin-icon"
      icon="mdi-cog-outline"
      :title="$t('Topbar.admin')"
      @click="openSettingsBox"
    />
    <v-menu location="bottom">
      <template #activator="{ props }">
        <v-btn
          data-cy="topbar-help"
          icon="mdi-help-circle-outline"
          :title="$t('Topbar.help')"
          v-bind="props"
        />
      </template>
      <v-list density="compact">
        <v-list-item
          data-cy="topbar-documentation-portal"
          :href="documentationPortalUrl"
          target="_blank"
        >
          <template #prepend>
            <v-icon>mdi-book-open-outline</v-icon>
          </template>
          <v-list-item-title>{{
            $t('Topbar.documentation_portal')
          }}</v-list-item-title>
        </v-list-item>
        <v-list-item
          data-cy="topbar-user-guide"
          :href="appStore.helpUrl"
          target="_blank"
        >
          <template #prepend>
            <v-icon>mdi-book-open-outline</v-icon>
          </template>
          <v-list-item-title>{{ $t('Topbar.user_guide') }}</v-list-item-title>
        </v-list-item>
        <v-list-item
          data-cy="topbar-need-help"
          :href="$config.NEED_HELP_URL"
          target="_blank"
        >
          <template #prepend>
            <v-icon>mdi-book-open-outline</v-icon>
          </template>
          <v-list-item-title>{{ $t('Topbar.need_help') }}</v-list-item-title>
        </v-list-item>
        <v-list-item data-cy="topbar-about" @click="openAboutBox">
          <template #prepend>
            <v-icon>mdi-information-outline</v-icon>
          </template>
          <v-list-item-title>{{ $t('Topbar.about') }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
    <v-menu v-if="isAuthenticated" offset-y>
      <template #activator="{ props }">
        <v-btn
          id="user-menu-btn"
          data-cy="topbar-user-name"
          class="ma-2 text-white"
          variant="text"
          v-bind="props"
        >
          <v-icon right class="mx-2"> mdi-account-outline </v-icon>
          {{ username }}
        </v-btn>
      </template>
      <v-list density="compact">
        <v-list-item v-if="authStore.userInfo">
          <template #prepend>
            <v-icon>mdi-security</v-icon>
          </template>
          <v-list-item-title>{{
            $t('_global.access_groups')
          }}</v-list-item-title>
          <v-list-item-subtitle
            v-for="(role, index) of authStore.userInfo.roles"
            :key="index"
          >
            {{ role }}
          </v-list-item-subtitle>
        </v-list-item>
        <v-list-item :to="{ name: 'Logout' }" data-cy="topbar-logout">
          <template #prepend>
            <v-icon>mdi-export</v-icon>
          </template>
          <v-list-item-title>{{ $t('_global.logout') }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
    <v-btn
      v-else
      id="login-btn"
      data-cy="topbar-login"
      class="text-capitalize mr-4"
      :to="{ name: 'Login' }"
      variant="text"
    >
      <v-icon>mdi-login</v-icon>
      {{ $t('_global.login') }}
    </v-btn>
    <div class="d-flex">
      <v-img
        class="mr-4"
        :src="nnLogoUrl"
        contain
        transition="scale-transition"
        width="50"
        height="50"
      />
    </div>
    <v-dialog v-model="showAboutDialog" max-width="1200">
      <AboutPage @close="showAboutDialog = false" />
    </v-dialog>
    <v-dialog
      v-model="settingsDialog"
      max-width="800"
      @keydown.esc="settingsDialog = false"
    >
      <SettingsDialog @close="settingsDialog = false" />
    </v-dialog>
    <ConfirmDialog ref="confirm" :text-cols="5" :action-cols="6">
      <template #actions>
        <v-btn
          color="nnBaseBlue"
          rounded="xl"
          elevation="2"
          @click="openSelectStudyDialog"
        >
          {{ $t('_global.select_study') }}
        </v-btn>
        <v-btn
          color="nnBaseBlue"
          rounded="xl"
          elevation="2"
          @click="redirectToStudyTable"
        >
          {{ $t('_global.add_study') }}
        </v-btn>
      </template>
    </ConfirmDialog>
    <v-dialog v-model="showSelectForm" persistent max-width="600px">
      <StudyQuickSelectForm
        @close="showSelectForm = false"
        @selected="reloadPage"
      />
    </v-dialog>
  </v-app-bar>
</template>

<script setup>
import { computed, inject, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { useAccessGuard } from '@/composables/accessGuard'
import { useStudiesGeneralStore } from '@/stores/studies-general'
import AboutPage from '@/components/layout/AboutPage.vue'
import ConfirmDialog from '@/components/tools/ConfirmDialog.vue'
import SettingsDialog from './SettingsDialog.vue'
import StudyQuickSelectForm from '@/components/studies/StudyQuickSelectForm.vue'
import { getAppEnv } from '@/utils/generalUtils'

const props = defineProps({
  hideAppBarNavIcon: {
    type: Boolean,
    default: false,
  },
})
const router = useRouter()
const emit = defineEmits(['backToRoot'])
const roles = inject('roles')
const $config = inject('$config')

const appStore = useAppStore()
const authStore = useAuthStore()
const studiesGeneralStore = useStudiesGeneralStore()
const { checkPermission } = useAccessGuard()
const sbLogoUrl = new URL(
  '../../assets/study_builder_homepage_logo.png',
  import.meta.url
).href
const nnLogoUrl = new URL(
  '../../assets/nn_logo_rgb_white_small.png',
  import.meta.url
).href

const appEnv = getAppEnv()

const selectedStudy = computed(() => studiesGeneralStore.selectedStudy)
const selectedStudyVersion = computed(
  () => studiesGeneralStore.selectedStudyVersion
)

const apps = [
  {
    icon: 'mdi-stethoscope',
    name: 'Studies',
    needsAuthentication: true,
  },
  {
    icon: 'mdi-bookshelf',
    name: 'Library',
    needsAuthentication: true,
  },
  {
    icon: 'mdi-wrench-outline',
    name: 'Administration',
    needsAuthentication: true,
    requiredRole: roles.ADMIN_WRITE,
  },
]

const showAboutDialog = ref(false)
const settingsDialog = ref(false)
const showSelectForm = ref(false)
const confirm = ref()

const documentationPortalUrl = computed(() => {
  return $config.DOC_BASE_URL
})
const username = computed(() => {
  return authStore.userInfo ? authStore.userInfo.name : 'Anonymous'
})
const isAuthenticated = computed(() => {
  return !$config.OAUTH_ENABLED || !!authStore.userInfo
})
const availableApps = computed(() => {
  return apps.filter(
    (app) =>
      !app.needsAuthentication ||
      (isAuthenticated.value &&
        (!app.requiredRole || checkPermission(app.requiredRole)))
  )
})
const currentStudyStatus = () => {
  if (!selectedStudy.value) {
    return null
  }
  return selectedStudy.value.current_metadata.version_metadata.study_status
}

function navigateToRoot() {
  emit('backToRoot')
}
function openAboutBox() {
  showAboutDialog.value = true
}
function openSettingsBox() {
  settingsDialog.value = true
}
function openSelectStudyDialog() {
  showSelectForm.value = true
}
function redirectToStudyTable() {
  confirm.value.cancel()
  router.push({ name: 'SelectOrAddStudy' })
}
function reloadPage() {
  const regex = /\/studies\/Study_[\d]+/
  const newUrl = document.location.href.replace(
    regex,
    '/studies/' + selectedStudy.value.uid
  )
  document.location.href = newUrl
}
</script>

<style scoped lang="scss">
@use 'vuetify/settings';
.action {
  cursor: pointer;
}
.v-toolbar {
  &-items {
    align-items: center;
    .v-btn {
      height: 60% !important;
      &--active {
        background-color: rgb(var(--v-theme-secondary));
        border-radius: settings.$border-radius-root * 2 !important;

        &::before {
          opacity: 0;
        }
      }
      &:hover {
        border-radius: settings.$border-radius-root * 2 !important;
      }
    }
  }
}
</style>
