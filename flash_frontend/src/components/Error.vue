<template>
    <div id="errors">
        <div>{{apiErrors[0]}}</div>
        <b-button squared class="mt-3 gradient" v-on:click="reloadPage()">Refresh page</b-button>
    </div>
</template>

<script>

    import { mapState, mapMutations } from "vuex"

    export default {
        name: "Error",
        computed: {
            ...mapState(["apiErrors"])
        },
        mounted() {
            this.stopLoading()
        },
        methods: {
            ...mapMutations(["startLoading", "stopLoading"]),
            reloadPage() {
                // Reload page on click
                this.$router.push("/session/")
                this.$router.go()
            }
        }
    }
</script>

<style scoped>

    #errors {
        position: absolute;
        width: 100vw;
        height: 100vh;
        top: 0px;
        font-size: 24px;
        font-weight: 700;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background-color: rgba(255, 255, 255, 0.8);
        z-index: 1;
        text-align: center;
    }

</style>