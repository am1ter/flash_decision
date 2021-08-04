<template>
    <div id='header_layout'>
        <div id='header_left'>
            <a class='header_button' href='#' >
                <img class='icon_margin_right' src='..\assets\icons\i_header_user.svg'/>
                <p class='text_no_margin'>{{ username }}</p>
            </a>
        </div>
        <div id='header_right'>
            <a class='header_button' href='#'>
                <img class='icon_margin_right' src='..\assets\icons\i_header_logout.svg'/>
                <p class='text_no_margin'>logout</p>
            </a>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Header',
    props: {
        username: {
            type: String,
            required: true,
            default: 'username'
        }
    }
}
</script>

<style>
    #header_layout {
        display: flex;
        flex-direction: row;
        width: 100%;
    }

    #header_left {
        width: 50%;
        text-align: left;
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
    }

    #header_right {
        width: 50%;
        text-align: right;
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
    }

    .header_button {
        display: flex;
        flex-direction: row;
    }

    .icon_margin_right {
        margin: 0px 5px 0px 0px;
    }

</style>