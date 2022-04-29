<template>
    <section id="header-layout">
        <div id="header-layout-fixed">
            <div id="header-top" v-if="isAuth">
                <div id="header-left">
                    <a class="header-button">
                        <img class="header-icon-left" src="../assets/icons/i_header_user.svg"/>
                        <p class="header-text-left">{{ user.email }}</p>
                    </a>
                </div>
                <div id="header-right">
                    <a id="button-logout" class="header-button" v-on:click="logout()">
                        <img class="header-icon-right" src="../assets/icons/i_header_logout.svg"/>
                        <p class="header-text-right">logout</p>
                    </a>
                </div>
            </div>
            <Menu/>
        </div>
        <Title id="title"/>
    </section>
</template>

<script>
    import { mapState, mapMutations } from "vuex"

    import Menu from "./subcomponents/Menu.vue"
    import Title from "./subcomponents/Title.vue"

    export default {
        name: "Header",
        components: {
            Menu,
            Title
        },
        props: {},
        computed: {
            ...mapState(["user"]),
            isAuth() {
                return this.$store.getters.isAuth
            }
        },
        methods: {
            ...mapMutations(["setNoUser"]),
            logout() {
                this.$store.commit("setNoUser")
                // Go to the login page
                this.$router.push("/login/")
            }
        }
}
</script>

<style>

    #header-layout-fixed {
        position: fixed;
        top: 0px;
        max-width: 453px;
        width: 100%;
        z-index: 2;
        background-color: #ffffff;
    }

    #header-top {
        display: flex;
        flex-direction: row;
        width: 100%;
        height: 35px;
    }

    #header-left {
        width: 50%;
        text-align: left;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
    }

    #header-right {
        width: 50%;
        text-align: right;
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
        align-items: center;
    }

    .header-button {
        display: flex;
        flex-direction: row;
        cursor: pointer;
    }

    .header-icon-left {
        margin: 0px 0px 0px 10px;
    }

    .header-icon-right {
        margin: 0px 5px 0px 0px;
    }

    .header-text-left {
        margin: 0px auto;
        padding: 0px 0px 0px 5px;
    }

    .header-text-right {
        margin: 0px auto;
        padding: 0px 10px 0px 0px;
    }

</style>