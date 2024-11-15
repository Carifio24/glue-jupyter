<template>
  <v-btn-toggle v-model="active_tool_id" class="transparent">
    <v-tooltip
      v-for="[id, {tooltip, img, dropdown, subtools}] of Object.entries(tools_data)"
      bottom
      :disabled="dropdown"
    >
      <template v-slot:activator="{ on }">
        <v-menu
          v-if="dropdown"
        >
          <template v-slot:activator="{ props }">
            <v-btn
              v-else
              v-on="on"
              icon
              :value="id"
            >
              <img :src="img" width="20" />
            </v-btn>
          </template>
          <v-btn
            v-for="subtool in subtools"
          >
            <img :src="subtool.img" width="20" />
          </v-btn>
        </v-menu>
        <v-btn
          v-else
          v-on="on"
          icon
          :value="id"
        >
            <img :src="img" width="20" />
        </v-btn>
      </template>
      <span>{{ tooltip }}</span>
    </v-tooltip>
  </v-btn-toggle>
</template>
