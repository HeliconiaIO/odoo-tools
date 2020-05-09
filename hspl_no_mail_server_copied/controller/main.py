# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.main import Database
from odoo.service import db
import logging
import odoo
from odoo import http
from odoo.http import dispatch_rpc, content_disposition
from bs4 import BeautifulSoup as Soup
from odoo import SUPERUSER_ID
from contextlib import closing
import os
import shutil
import re
import json
import zipfile
import datetime
import tempfile
import werkzeug

_logger = logging.getLogger(__name__)
DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'


def new_exp_duplicate_database(db_original_name, db_name, no_mail_server_info):
    _logger.info('1111Duplicate database `%s` to `%s` no_mail_server_info: `%s`.', db_original_name, db_name,
                 no_mail_server_info)
    odoo.sql_db.close_db(db_original_name)
    x_db = odoo.sql_db.db_connect('postgres')
    with closing(x_db.cursor()) as cr:
        cr.autocommit(True)  # avoid transaction block
        db._drop_conn(cr, db_original_name)
        cr.execute("""CREATE DATABASE "%s" ENCODING 'unicode' TEMPLATE "%s" """ % (db_name, db_original_name))

    registry = odoo.modules.registry.Registry.new(db_name)
    with registry.cursor() as cr:
        # if it's a copy of a database, force generation of a new dbuuid
        env = odoo.api.Environment(cr, SUPERUSER_ID, {})
        env['ir.config_parameter'].init(force=True)
        if no_mail_server_info:
            env['fetchmail.server'].search([]).unlink()
            env['ir.mail_server'].search([]).unlink()

    from_fs = odoo.tools.config.filestore(db_original_name)
    to_fs = odoo.tools.config.filestore(db_name)
    if os.path.exists(from_fs) and not os.path.exists(to_fs):
        shutil.copytree(from_fs, to_fs)
    return True


def new_dump_db(db_name, stream, backup_format='zip'):
    cmd = ['pg_dump', '--no-owner', '--exclude-table-data=*fetchmail_server', '--exclude-table-data=*ir_mail_server']
    cmd.append(db_name)

    if backup_format == 'zip':
        with odoo.tools.osutil.tempdir() as dump_dir:
            filestore = odoo.tools.config.filestore(db_name)
            if os.path.exists(filestore):
                shutil.copytree(filestore, os.path.join(dump_dir, 'filestore'))
            with open(os.path.join(dump_dir, 'manifest.json'), 'w') as fh:
                database = odoo.sql_db.db_connect(db_name)
                with database.cursor() as cr:
                    json.dump(db.dump_db_manifest(cr), fh, indent=4)
            cmd.insert(-1, '--file=' + os.path.join(dump_dir, 'dump.sql'))
            odoo.tools.exec_pg_command(*cmd)
            if stream:
                odoo.tools.osutil.zip_dir(dump_dir, stream, include_dir=False,
                                          fnct_sort=lambda file_name: file_name != 'dump.sql')
            else:
                t = tempfile.TemporaryFile()
                odoo.tools.osutil.zip_dir(dump_dir, t, include_dir=False,
                                          fnct_sort=lambda file_name: file_name != 'dump.sql')
                t.seek(0)
                return t
    else:
        cmd.insert(-1, '--format=c')
        stdin, stdout = odoo.tools.exec_pg_command_pipe(*cmd)
        if stream:
            shutil.copyfileobj(stdout, stream)
        else:
            return stdout


db.exp_duplicate_database = new_exp_duplicate_database


class MyDatabase(Database):

    def _render_template(self, **d):
        res = super(MyDatabase, self)._render_template(**d)
        soup = Soup(res, features="html.parser")
        dupli_form = soup.find(id="form-duplicate-db")
        backup_form = soup.find(id="form_backup_db")
        if dupli_form:
            body_div = dupli_form.find("div")
            if body_div:
                bool_mail_data_str = """
                    <div class="form-group form-check">
                        <label for="no_mail_server_info" class="control-label">No Mail Server Info</label>
                        <br/>
                        <input id="no_mail_server_info" type="checkbox" name="no_mail_server_info" class="form-check-input" title="Don't copy incoming / outgoing mail server information."/>
                        <label class="form-check-label" for="no_mail_server_info" >Don't copy incoming / outgoing mail server information.</label>
                    </div>
                """
                mail_data = Soup(bool_mail_data_str, features="xml")
                body_div.append(mail_data)
                res = unicode(soup)
        if backup_form:
            body_div = backup_form.find("div")
            if body_div:
                bool_mail_data_str = """
                    <div class="form-group form-check">
                        <label for="no_mail_server_info" class="control-label">No Mail Server Info</label>
                        <br/>
                        <input id="no_mail_server_info" type="checkbox" name="no_mail_server_info" class="form-check-input" title="Don't copy incoming / outgoing mail server information."/>
                        <label class="form-check-label" for="no_mail_server_info" >Don't copy incoming / outgoing mail server information.</label>
                    </div>
                """
                mail_data = Soup(bool_mail_data_str, features="xml")
                body_div.append(mail_data)
                res = unicode(soup)
        return res

    @http.route('/web/database/duplicate', type='http', auth="none", methods=['POST'], csrf=False)
    def duplicate(self, master_pwd, name, new_name, **post):
        try:
            if not re.match(DBNAME_PATTERN, new_name):
                raise Exception(
                    _('Invalid database name. Only alphanumerical characters, underscore, hyphen and dot are allowed.'))
            no_mail_server_info = False
            if post.get("no_mail_server_info", False) == "on":
                no_mail_server_info = True
            dispatch_rpc('db', 'duplicate_database', [master_pwd, name, new_name, no_mail_server_info])
            return http.local_redirect('/web/database/manager')
        except Exception as e:
            error = "Database duplication error: %s" % (str(e) or repr(e))
            return self._render_template(error=error)

    @http.route('/web/database/backup', type='http', auth="none", methods=['POST'], csrf=False)
    def backup(self, master_pwd, name, backup_format='zip', **post):
        try:
            odoo.service.db.check_super(master_pwd)
            ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            filename = "%s_%s.%s" % (name, ts, backup_format)
            headers = [
                ('Content-Type', 'application/octet-stream; charset=binary'),
                ('Content-Disposition', content_disposition(filename)),
            ]
            if post.get("no_mail_server_info", False) == "on":
                dump_stream = new_dump_db(name, None, backup_format)
            else:
                dump_stream = odoo.service.db.dump_db(name, None, backup_format)
            response = werkzeug.wrappers.Response(dump_stream, headers=headers, direct_passthrough=True)
            return response
        except Exception as e:
            _logger.exception('Database.backup')
            error = "Database backup error: %s" % (str(e) or repr(e))
            return self._render_template(error=error)
