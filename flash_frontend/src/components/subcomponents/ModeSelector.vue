<template>
    <!-- Navigation bar (modes) -->
    <div id="session-mode" v-if="!isLoading">
        <ul class="nav justify-content-center mb-4">
            <li id="button-mode-custom" class="nav-item">
                <a class="nav-link" 
                :class="{active: isPageActive('custom')}"
                role="button"
                v-on:click="$router.push(`/${page}/custom/${userIdUrl()}`)">Custom</a>
            </li>
            <li id="button-mode-classic" class="nav-item">
                <a class="nav-link" 
                :class="{active: isPageActive('classic')}" 
                role="button" 
                v-on:click="$router.push(`/${page}/classic/${userIdUrl()}`)">Classic</a>
            </li>
            <li id="button-mode-blitz" class="nav-item">
                <a class="nav-link"
                :class="{active: isPageActive('blitz')}"
                role="button"
                v-on:click="$router.push(`/${page}/blitz/${userIdUrl()}`)">Blitz</a>
            </li>
            <li id="button-mode-crypto" class="nav-item">
                <a class="nav-link" 
                :class="{active: isPageActive('crypto')}" 
                role="button" 
                v-on:click="$router.push(`/${page}/crypto/${userIdUrl()}`)">Crypto</a>
            </li>
        </ul>
    </div>
</template>

<script>
    import { mapState } from "vuex"

    export default {
        name: "ModeSelector",
        data() {
            return {}
        },
        props: {
            page: String,
            userId: String
        },
        computed: {
            ...mapState(["user", "currentSession", "isLoading"])
        },
        beforeMount() {},
        methods: {
            isPageActive(nav_item) {
                // Check if navbar item is active
                return this.$route.params.mode == nav_item
            },
            userIdUrl() {
                return (this.userId == undefined) ? "" : this.userId
            }
        }
    }

</script>

<style scoped>

</style>
