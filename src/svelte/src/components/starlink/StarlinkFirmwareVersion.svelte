<script>
    import {starlinkStatus} from "../../stores";
</script>
<div style="display:flex; flex-flow: column;justify-content: center;">
    <span class="mediumSmallText">Fw: {$starlinkStatus?.software_version ? $starlinkStatus?.software_version : 'UNKNOWN'}</span>
</div>
