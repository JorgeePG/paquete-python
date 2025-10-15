import responses  # type: ignore
from t8_client import BASE_URL, T8ApiClient 

@responses.activate
def test_login_success()->None:
    responses.add(
        responses.POST,
        "https://lzfs45.mirror.twave.io/lzfs45/signin",
        json={"token":"test_token","success":True, "text":"Todo bien"},
        status=200,
    )
    client = T8ApiClient()

    assert client.login_with_credentials("user","pass")

@responses.activate
def test_login_invalid_credentials()->None:
    responses.add(
        responses.POST,
        "https://lzfs45.mirror.twave.io/lzfs45/signin",
        body="Invalid Username or Password",
        status=200,
    )
    client = T8ApiClient()

    assert not client.login_with_credentials("user","wrong_pass")


@responses.activate
def test_login_server_error()->None:
    responses.add(
        responses.POST,
        "https://lzfs45.mirror.twave.io/lzfs45/signin",
        body="Internal Server Error",
        status=500,
    )
    client = T8ApiClient()

    assert not client.login_with_credentials("user","pass")

@responses.activate
def test_login_exception()->None:
    responses.add(
        responses.POST,
        "https://lzfs45.mirror.twave.io/lzfs45/signin",
        body=Exception("Connection error")
    )
    client = T8ApiClient()

    assert not client.login_with_credentials("user","pass")

@responses.activate
def test_get_waveform_success()->None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "waves/test_machine/test_point/test_proc_mode",
        json={
    "_links": {
        "home": "http://lzfs45.mirror.twave.io/lzfs45/rest/",
        "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/test_machine/test_point/test_proc_mode/0"
    },
    "data": "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",  # noqa: E501
    "factor": 0.03800759,
    "path": "test_machine:test_point:test_proc_mode",
    "sample_rate": 5120,
    "snap_t": 1555119736.011538,
    "speed": 2.034545,
    "t": 1555119735.2103505,
    "unit_id": 14
    },
        status=200,
    )
    assert client.list_waves("test_machine", "test_point", "test_proc_mode")

@responses.activate
def test_get_waveform_failure()->None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "waves/test_machine/test_point/test_proc_mode",
        body="Not Found",
        status=404,
    )
    assert not client.list_waves("test_machine", "test_point", "test_proc_mode")

@responses.activate
def test_get_spectra_success()->None:
    client =T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "spectra/test_machine/test_point/test_proc_mode",
        json={
    "_links": {
        "home": "http://lzfs45.mirror.twave.io/lzfs45/rest/",
        "self": "http://lzfs45.mirror.twave.io/lzfs45/rest/waves/test_machine/test_point/test_proc_mode/0"
    },
    "data": "eJw01mlwXeV5B/Dfe+7VYm1X+66rzde6lixZUiRrsSVbsmQjI8V4Be/FhmGpcQ0m9jhkHNuxywAxIWRowE4bSNOShg8pcZoOodNCErbSKZMPMaQpw3RJZ5LSTppJuqfp6J127oc7c8573mf7L89/h68mTyTNhf+a/HH4RXgp/GrqV59MZp/3pJ+kfpC6lEyH8XAiOZB8LrxWtSX/1/V3Jw8nt4fjfj/8XvjQh95Lvp0MF3695OGCgfA39poK9WFCEt532W+7XnCy/ImiZ/yF/3QmlIRx3/IlfS4YLDqUWSj+u/CorT5pIPy7dSb8wi9NpBdLZgvv8pgHDdjhDnPOO+gd08mPC/4r9V05jfpt1mfcoFu96N3kC4V96Vets1uzZ3zXKZ+VsWA+qSr4g9Q1GRmNunVYcKd52+0Kf5Y6mlx0xbOWfM67Pm/En3vCH4Yt6fHUPeG4M9bY4z5DsqZ84M3QUVCcfluvcbMGjWpVZ5VnzSVXCm8tWAy7ZbUo1WajYy640+vhjfSNVCpsdcA+W+SttM2AI06EV1M3pd63wagWHSrkbTPqbrvC0VRNqiJkdUkpktKmQM4L7k62Fr5c8NNw3CotajTJadeuzzs6klTyR/JKlcvL6Zaxzin/ED5Mv5V+LbyoTJd+GRVWKDTicaOhN9yvUZ8qo7pVKtTnqp+Gb6VfT1cmT1mpXoNmJSq0e8gXw+nUx1OHwycM6Tem04z75Kz3M19KulN3hTes9lG9Vlirz4Av+9twa/qb6buSr9uuWbN++83EavvCc8lPkvvDeSM6lcioVCXn0zaFf0q2p94OX5Q3pE6ZRmXqPebXQ3vqYurvw7umlUppjdmt96iXw+OppvRc8h03a1evRqlqG33FjfCPqa+lryf58Bv6zahULaPVYemQTT6VXAyXTGpSGTNokDPtO66HTLIhfMKgemWq1AiGXHJHeCWZTzUkP3JYm3JFimWsMe9ND4XXw5rwkLwGdQql1Rix07uuhBthMjxtqyJlipSqNexBubAxeSX5cfgfRw0pVC1EVPXY43e943es16VIrURauX5n/Mw3Q3tyLbzhgJw6RQqUGXXIE0bDw2EgXLVFVexYgWY55zSEn4eTyb+ETDhsINZTpk2laXd43p961gkzChQrklai2SZPaQ1HQ0f4smmtEnUyCvTZ4QOXw41wKXzgtB7N8YtGOTd70ZbwSNgR3nevbjXSCq2w2pIn1YfFUB++4YCsVTKKFWgy7airXvC0Y0aVKlauWKEKdSoMGTesSVaRElUqtBi137cthMfC0fChj5vWqFSZcqWG7HXJcz7vuAUZ1TH+CjPOyYTnwr+F98Js+IqFyIUC9SoNO+tVP/SXrtlrpSorlKhUbMoDvup1L/m0W9SpUaxShWIrNOgzYsiAdiUxeplqTXa46j1F4Ze+4YzNGmWkNFvtmBeUhukwHP7ZZdNWq5AIinTYZr8DttscT9YqjV8NOeEt2bAtbA2V4Rn7DWtRpliNTU667nte84xDPhIZUqpInWaNlux3yKJhnVETCpWpNWKH8676lAfskddohUoFetzmvOs+8COvumxOi1rlKnXZ6TPe9HP/4Ye+4LAuZcrUqdep3pydFs0Z1aQmYqpDpyWnveyG73vRJdv1RNQvq9ycPU674kmnLdiiT7kSWXk3edjXfM/73vaIW4ypV6HBKrPu9ZK3vOJ5j9htQK3q2O9W43bbaZ/t1hgwqFSBGi2qdJu1YFzOQMxtWS1C1ITWGK9ZrS41UWHLpGMtR5xyxTWfddykfGT+chdGHHHYx/yms/Yat0a5ci1KNOmLv4/E6MuTW6FAnZUabXS7Y+5wZFnrZHVH3qXUyWrTbsCIvFZN8WmDjAYTxkzYZNbayLdyTVaoUqrTenPmzRuT1xlnVxGrXWnKRptttTbOvk6tinhjq1VW69Or38r/e14RHTRvt2OO2me3Teo0xuktdyZjwKwZU3pVqVYREV+tXrlGtWoVq5dVJURGthkwZ4sdTjgVHbtDQ6yvUaO8CR+x0W4L0UkrI4caFMro0avXoA5tGpRLZNTJucVexxzxa47YEfWvQomiOLm8blnNenQojzq+XOWw7fZ7wIPudqt9ZjXGWspVxPn3GjKsX5dGnVJK4h7Rq8+UBUs+akybJhlpXZqt1W+tIetNG45u8v9zzenVbcC0icj8ZZVf1v8W3VriyWa9BpRG7CzXuM4u9zjrnLPuc6eDJqNvdMjbaNEOt7nZZjNRefqlDZoyYcmi/e51zD7zpqIvdet1swOOOOSgHRZNyOqMnt6iNTpur0591qjSpMtKPUpj17N6jVkvr1JnrLZQs1atOvTE/05ZFWqwzmzkwkUXnXPSvQ5aa0SdHtVqlMsoi1GXMdqlU4sewzbaYM6sTTabN22jKbVWyemx1owle+y0ybA+NRE71fq16zdpwoIZY0pljZp02eP+xA/8le97y3WfccHtthjUa6ch2x2x3zazpozoNqxVTpfhGHebOZPG45tRVQaN2+w2+xxywB6TcYOpt0qT0ph9l5xybbGL9fosOeaU8570tGuueSR2Ymvc+5Z3qXRU20qVUXF7Iio7Lbrfo37LUy643z3utM+0Nmt1WRP7sEq31VZGLnap1G3QvG1uss/t9lu0y6Qu5eqjD9briudSmiJCl3eEnKxB620wZUy/NSZ02KLSrDkHnXTSWQ854x63xNuzxhWYMWq9iYjvMR2xA5PWmrDLEedc8DEXPeaUJdsNG5M1YcKkOTcZi8qzvCkNatdp2AbzZixaNGudpXhzSrcuY9YYMmaDcev0Wq/NAfMORz383wAAAP//ya6rqA==",  # noqa: E501
    "factor": 0.000102270635,
    "max_freq": 250,
    "min_freq": 0.625,
    "path": "LP_Turbine:MAD32CY005:AM2",
    "snap_t": 1555119736.011538,
    "speed": 2.034545,
    "t": 1555119729.402038,
    "unit_id": 14,
    "window": 1
},
        status=200,
    )
    assert client.list_spectra("test_machine", "test_point", "test_proc_mode")

@responses.activate
def test_get_spectra_failure()->None:
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "spectra/test_machine/test_point/test_proc_mode",
        body="Not Found",
        status=404,
    )
    assert not client.list_spectra("test_machine", "test_point", "test_proc_mode")

@responses.activate
def test_get_wave()->None:
    url = (BASE_URL + "waves/" + machine + "/" + point + "/" + 
            procMode + "/" + str(timestamp))
    client = T8ApiClient()
    responses.add(
        responses.GET,
        BASE_URL + "waves/test_machine/test_point/test_proc_mode",
        json={