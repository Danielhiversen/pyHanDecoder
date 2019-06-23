import base64
import datetime
import logging

_LOGGER = logging.getLogger(__name__)


def decode_kaifa(buf, log=False):
    """Decode kaifa."""
    # pylint: disable=too-many-instance-attributes, too-many-branches
    if buf[10:12] != '10':
        if log:
            _LOGGER.error("Unknown control field %s", buf[10:12])
        return None
    try:
        if int(buf[1:4], 16) * 2 != len(buf):
            if log:
                _LOGGER.error("Invalid length %s, %s", int(buf[1:4], 16) * 2, len(buf))
            return None

        buf = buf[32:]
        txt_buf = buf[28:]
        if txt_buf[:2] != '02':
            if log:
                _LOGGER.error("Unknown data %s", buf[0])
            return None

        year = int(buf[4:8], 16)
        month = int(buf[8:10], 16)
        day = int(buf[10:12], 16)
        hour = int(buf[14:16], 16)
        minute = int(buf[16:18], 16)
        second = int(buf[18:20], 16)
        date = "%02d%02d%02d_%02d%02d%02d" % (second, minute, hour, day, month, year)

        res = {}
        res['time_stamp'] = datetime.strptime(date, '%S%M%H_%d%m%Y')

        pkt_type = txt_buf[2:4]
        txt_buf = txt_buf[4:]
        if pkt_type == '01':
            res['Effect'] = int(txt_buf[2:10], 16)
        elif pkt_type in ['09', '0D', '12', '0E']:
            res['Version identifier'] = base64.b16decode(txt_buf[4:18]).decode("utf-8")
            txt_buf = txt_buf[18:]
            res['Meter-ID'] = base64.b16decode(txt_buf[4:36]).decode("utf-8")
            txt_buf = txt_buf[36:]
            res['Meter type'] = base64.b16decode(txt_buf[4:20]).decode("utf-8")
            txt_buf = txt_buf[20:]
            res['Effect'] = int(txt_buf[2:10], 16)
            if pkt_type in ['12', '0E']:
                txt_buf = txt_buf[10:]
                txt_buf = txt_buf[78:]
                res['Cumulative_hourly_active_import_energy'] = int(txt_buf[2:10], 16)
                txt_buf = txt_buf[10:]
                res['Cumulative_hourly_active_export_energy'] = int(txt_buf[2:10], 16)
                txt_buf = txt_buf[10:]
                res['Cumulative_hourly_reactive_import_energy'] = int(txt_buf[2:10], 16)
                txt_buf = txt_buf[10:]
                res['Cumulative_hourly_reactive_export_energy'] = int(txt_buf[2:10], 16)
        else:
            if log:
                _LOGGER.warning("Unknown type %s", pkt_type)
            return None
    except ValueError:
        if log:
            _LOGGER.error("Failed", exc_info=True)
        return None
    return res


def decode_aidon(buf, log=False):
    """Decode Aidon."""
    if buf[10:12] != '13':
        if log:
            _LOGGER.error("Unknown control field %s", buf[10:12])
        return None

    try:
        if int(buf[1:4], 16) * 2 != len(buf):
            if log:
                _LOGGER.error("Invalid length %s, %s", int(buf[1:4], 16) * 2, len(buf))
            return None

        res = {}
        res['time_stamp'] = None
        pkt_type = buf[36:38]
        if pkt_type == '01':
            res['Effect'] = int(buf[60:68], 16)
        elif pkt_type in ['09', '0C', '0D', '0E', '11', '12']:
            res['Effect'] = int(buf[194:202], 16)
        else:
            if log:
                _LOGGER.warning("Unknown type %s", pkt_type)
            return None
    except ValueError:
        if log:
            _LOGGER.error("Failed", exc_info=True)
        return None
    return res


def decode_kamstrup(buf, log=False):
    """Decode Kamstrup."""
    if buf[8:10] != '13':
        if log:
            _LOGGER.error("Unknown control field %s", buf[10:12])
        return None
    if len(buf) < 176:
        if log:
            _LOGGER.error("Data length %s", len(buf))
        return None
    buf = buf[32:]
    txt_buf = buf[26:]

    pkt_type = txt_buf[0:2]
    if pkt_type not in ['0F', '11', '1B', '17', '21', '19', '23']:
        if log:
            _LOGGER.warning("Unknown type %s", pkt_type)
        return None

    try:
        year = int(buf[0:4], 16)
        month = int(buf[4:6], 16)
        day = int(buf[6:8], 16)
        hour = int(buf[10:12], 16)
        minute = int(buf[12:14], 16)
        second = int(buf[14:16], 16)
        date = "%02d%02d%02d_%02d%02d%02d" % (second, minute, hour, day, month, year)

        res = {}
        res['time_stamp'] = datetime.strptime(date, '%S%M%H_%d%m%Y')
        res['Effect'] = int(txt_buf[160:168], 16)
    except ValueError:
        if log:
            _LOGGER.error("Failed", exc_info=True)
        return None
    return res
