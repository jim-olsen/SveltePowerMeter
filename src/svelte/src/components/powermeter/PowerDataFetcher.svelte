<script>
    //
    // This component provides for the fetching of data from the python flask server for all of the different data records.
    // This is done centrally so the timing is consistent between components and the fetches are reduced by sharing the
    // data between all components.  Any component wanting data should subscribe to this datasource
    //
    import {powerStatsData} from "../../stores";
    import {powerGraphData} from "../../stores";
    import {powerCurrentData} from "../../stores";

    function getStatsData() {
        fetch("/statsData", {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(d => {
                $powerStatsData = d;
            });
    }

    function getGraphData() {
        fetch("/graphData", {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(d => {
                $powerGraphData = d;
            });
    }

    function getCurrentData() {
        fetch("/currentData", {
            headers: {
                "Accept": "application/json"
            }
        })
            .then(d => d.json())
            .then(d => {
                $powerCurrentData = d;
            });
    }

    let statsInterval;
    $: {
        clearInterval(statsInterval);
        statsInterval = setInterval(getStatsData, 5000);
    }
    let graphInterval;
    $: {
        clearInterval(graphInterval);
        graphInterval = setInterval(getGraphData, 5000);
    }
    let currentInterval;
    $: {
        clearInterval(currentInterval);
        currentInterval = setInterval(getCurrentData, 5000)
    }
</script>