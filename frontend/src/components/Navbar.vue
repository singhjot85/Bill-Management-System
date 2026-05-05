<template>
  <v-app-bar 
    :flat="flat" 
    :border="border" 
    :color="color" 
    :class="['px-md-6 px-4', customClass]"
    :fixed="fixed"
    :app="app"
  >
    <!-- Left side elements -->
    <div class="d-flex align-center">
      <template v-for="(item, index) in leftItems" :key="'left-' + index">
        <component
          :is="getComponent(item.type)"
          v-bind="getComponentProps(item)"
          v-on="getComponentEvents(item)"
        >
          <!-- Handle icon-button and button content -->
          <template v-if="item.type === 'icon-button' || item.type === 'button'">
            <v-icon v-if="item.metadata.icon || item.metadata.iconResolver" :class="getDisplayText(item) ? 'mr-2' : ''">
              {{ getIcon(item) }}
            </v-icon>
            <span v-if="getDisplayText(item)">{{ getDisplayText(item) }}</span>
          </template>

          <!-- Handle pure text content -->
          <template v-else-if="item.type === 'text'">
            {{ getDisplayText(item) }}
          </template>
        </component>
      </template>
    </div>

    <v-spacer />

    <!-- Right side elements -->
    <div class="d-flex align-center">
      <template v-for="(item, index) in rightItems" :key="'right-' + index">
        <component
          :is="getComponent(item.type)"
          v-bind="getComponentProps(item)"
          v-on="getComponentEvents(item)"
        >
          <!-- Handle icon-button and button content -->
          <template v-if="item.type === 'icon-button' || item.type === 'button'">
            <v-icon v-if="item.metadata.icon || item.metadata.iconResolver" :class="getDisplayText(item) ? 'mr-2' : ''">
              {{ getIcon(item) }}
            </v-icon>
            <span v-if="getDisplayText(item)">{{ getDisplayText(item) }}</span>
          </template>

          <!-- Handle pure text content -->
          <template v-else-if="item.type === 'text'">
            {{ getDisplayText(item) }}
          </template>
        </component>
      </template>
    </div>
  </v-app-bar>
</template>

<script setup>
import { computed } from 'vue';
import { useBrandingStore } from '@/stores/brandingStore';
import { defaultNavbarConfig } from '@/config/navbarConfig';

const props = defineProps({
  branding: Object,
  config: {
    type: Object,
    default: () => defaultNavbarConfig
  },
  flat: { type: Boolean, default: true },
  border: { type: Boolean, default: true },
  color: { type: String, default: 'surface' },
  customClass: { type: String, default: '' },
  fixed: { type: Boolean, default: false },
  app: { type: Boolean, default: true }
});

const emit = defineEmits(['action', 'navigate']);
const brandingStore = useBrandingStore();

const resolvers = {
  getThemeIcon: () => brandingStore.theme === 'dark' ? 'mdi-white-balance-sunny' : 'mdi-moon-waning-crescent',
  getTenantName: () => props.branding?.tenantName || brandingStore.tenantName,
  getLoginText: () => brandingStore.isPrivateFlow ? 'Dashboard' : 'Login/Signup'
};

const getIcon = (item) => {
  const resolver = item.metadata.iconResolver;
  if (resolver && resolvers[resolver]) {
    return resolvers[resolver]();
  }
  return item.metadata.icon;
};

const getDisplayText = (item) => {
  const resolver = item.metadata.textResolver;
  if (resolver && resolvers[resolver]) {
    return resolvers[resolver]();
  }
  return item.metadata.text;
};

const leftItems = computed(() => {
  return props.config.leftItems.map(item => {
    const newItem = JSON.parse(JSON.stringify(item));
    if (newItem.type === 'image' && !newItem.metadata.url) {
      newItem.metadata.url = props.branding?.logoUrl || brandingStore.logoUrl;
    }
    if (newItem.type === 'text' && !newItem.metadata.text && !newItem.metadata.textResolver) {
      newItem.metadata.textResolver = 'getTenantName';
    }
    return newItem;
  });
});

const rightItems = computed(() => {
  return props.config.rightItems.map(item => {
    const newItem = JSON.parse(JSON.stringify(item));
    return newItem;
  });
});

const getComponent = (type) => {
  switch (type) {
    case 'image': return 'v-img';
    case 'text': return 'div';
    case 'button': return 'v-btn';
    case 'icon-button': return 'v-btn';
    case 'spacer': return 'v-spacer';
    default: return 'div';
  }
};

const getComponentProps = (item) => {
  const meta = item.metadata;
  const commonProps = {
    class: meta.class,
    style: meta.clickable ? { cursor: 'pointer' } : {}
  };

  switch (item.type) {
    case 'image':
      return {
        ...commonProps,
        src: meta.url,
        width: meta.width,
        height: meta.height,
        cover: true
      };
    case 'button':
      return {
        ...commonProps,
        variant: meta.variant,
        // Removed 'to' to handle navigation via emit if desired, or keep for simple links
        // If we want total control in parent, we remove 'to' and use click event
        color: meta.color,
        size: meta.size,
        icon: (!!meta.icon || !!meta.iconResolver) && !getDisplayText(item),
        class: [meta.class, 'text-none'].join(' ')
      };
    case 'icon-button':
      return {
        ...commonProps,
        icon: true,
        size: meta.size || 'small',
        color: meta.color
      };
    case 'text':
      return {
        ...commonProps,
        style: {
          ...commonProps.style,
          whiteSpace: 'nowrap'
        }
      };
    default:
      return commonProps;
  }
};

const getComponentEvents = (item) => {
  const events = {};
  
  if (item.metadata.action || item.metadata.to || item.metadata.clickable) {
    events.click = (e) => {
      e.stopPropagation();
      if (item.metadata.action) {
        emit('action', item.metadata.action, item);
      } else if (item.metadata.to) {
        emit('navigate', item.metadata.to, item);
      }
    };
  }
  
  return events;
};
</script>
