<template>
    <div>
        <div>
            <v-select :items="x_att_items" label="x axis" v-model="x_att_selected"/>
        </div>
        <div>
            <v-text-field type="number" step="1" label="number of bins" v-model="glue_state.hist_n_bin" />
        </div>
        <div>
            <glue-float-field label="x-min" :value.sync="glue_state.hist_x_min" />-->
        </div>
        <div>
            <glue-float-field label="x-max" :value.sync="glue_state.hist_x_max" />-->
        </div>
        <div>
            <v-toolbar density="compact" >
                  <v-tooltip>
                    <template v-slot:activator="{ on }">
                         <v-btn v-on="on" size="x-small" value="normalize">
                             <v-icon>unfold_more</v-icon>
                         </v-btn>
                     </template>
                    <span>normalize</span>
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on }">
                        <v-btn v-on="on" size="x-small" value="cumulative">
                            <v-icon>trending_up</v-icon>
                        </v-btn>
                    </template>
                    <span>cumulative</span>
                  </v-tooltip>

                  <v-btn variant="outlined" size="x-small" @click="bins_to_axes">
                      Fit Bins to Axes
                  </v-btn>
            </v-toolbar>
        </div>
        <v-switch v-model="glue_state.show_axes" label="Show axes" hide-details/>
    </div>
</template>
<script>
    module.exports = {
        computed: {
            modeSet() {
                return [this.glue_state.normalize && 'normalize', this.glue_state.cumulative && 'cumulative']
            }
        },
        methods: {
            modeSetChange(v) {
                this.glue_state.normalize = v.includes('normalize');
                this.glue_state.cumulative = v.includes('cumulative');
            }
        }
    }
</script>
