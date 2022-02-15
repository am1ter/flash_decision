<template>
    <section id='page'>
        <div v-if="apiErrors.length == 0 & isLoaded" class="text-center shadow col-12 pt-2">
            <h1>N/A</h1>
            <p>
                Nobody has tried this mode yet<br>
                Will you be the first one?
            </p>
        </div>
    </section>
</template>

<script>
    import { mapState } from 'vuex'
    import { apiGetScoreboard } from '@/api'

    export default {
        name: 'page_Scoreboard',
        data() {
            return {
                isLoaded: false,
            }
        },
        computed: {
            ...mapState(['user', 'currentSession', 'apiErrors'])
        },
        mounted() {
            this.loadScoreboard()
        },
        methods: {
            async loadScoreboard() {
                // Load last session results
                let response = await apiGetScoreboard(this.user.id)
                console.log(response)
                this.isLoaded = true
            }
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
