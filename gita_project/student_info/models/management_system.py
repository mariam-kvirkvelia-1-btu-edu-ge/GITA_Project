import base64
from io import BytesIO

from odoo.exceptions import UserError
from odoo import models, fields, api, registry, tools, _
import logging
from xlsxwriter import Workbook
import os

_logger = logging.getLogger(__name__)

class StudentInformation(models.Model):
    _name = 'student.information'
    _description = 'Student management system'


    name = fields.Char(string='სრული სახელი', compute="compute_full_name")
    first_name_student = fields.Char(string='სახელი')
    last_name_student = fields.Char(string='გვარი')
    id_number = fields.Integer(string='პირადი ნომერი')
    gender = fields.Selection(selection=[('1', 'მამრობითი'),('2', 'მდედრობითი')], string='სქესი')
    birth_date = fields.Date(string='დაბადების თარიღი')
    image = fields.Binary(string='student image')
    parent_name = fields.Char(string='მშობლის სახელი')
    mobile = fields.Char(string='მშობლის მობილურის ნომერი')
    address = fields.Char(string='მისამართი')
    roll_number_student = fields.Integer(string='სიის ნომერი')
    grade_student = fields.Selection(selection=[('a', 'A'),('b', 'B'),('c', 'C'),('d', 'D'),('e', 'E'),('fx', 'FX')], string='შეფასება')

    excel_file = fields.Binary(string='დაგენერირებული ფაილი', attachment=True)

    def report(self):

        results = eval('self.generate_report')
        self.write({'excel_file': 'excel_file', 'excel_filename': 'filename'})
        attachment = self.env['ir.attachment'].create({
            'datas': results.get('excel_file'),
            'name': results.get('filename'),
            'datas_fname': results.get('filename'),
            'type': 'binary',
        })
        generated_report_values = {
            'file': [(4, attachment.id)],
        }
        # self.env['student.generate.report'].create(generated_report_values)

    @api.depends('first_name_student', 'last_name_student')
    def compute_full_name(self):
        for rec in self:
            if rec.first_name_student and rec.last_name_student:
                rec.name = f" {rec.first_name_student} {rec.last_name_student}"
            else:
                rec.name = ""

class AddStudent(models.Model):
    _inherit = 'res.partner'

    full_name = fields.Char(compute='compute_full_name', store=True)
    name = fields.Char(string='სახელი')
    last_name = fields.Char(string='გვარი')
    id_number = fields.Integer(string='პირადი ნომერი')
    gender = fields.Selection(selection=[('1', 'მამრობითი'),('2', 'მდედრობითი')], string='სქესი')
    birth_date = fields.Date(string='დაბადების თარიღი')
    image = fields.Binary(string='student image')
    parent_name = fields.Char(string='მშობლის სახელი')
    mobile = fields.Char(string='მშობლის მობილურის ნომერი')
    address = fields.Char(string='მისამართი')
    roll_number = fields.Integer(string='სიის ნომერი')
    grade_student = fields.Selection(selection=[('a', 'A'),('b', 'B'),('c', 'C'),('d', 'D'),('e', 'E'),('fx', 'FX')], string='შეფასება')
    files = fields.Many2many('ir.attachment')


    @api.depends('name', 'last_name')
    def compute_full_name(self):
        for rec in self:
            if rec.name and rec.last_name:
                rec.full_name = f" {rec.name} {rec.last_name}"
            else:
                rec.full_name = ""

    def addstud(self):
        for rec in self:
            record = self.env['student.information']
            record.create({
                'first_name_student': rec.name,
                'roll_number_student': rec.roll_number,
                'grade_student': rec.grade_student,
                'image': rec.image,
                'last_name_student': rec.last_name,
                'name': rec.full_name,
                'mobile': rec.mobile,
                'address': rec.address,
                'parent_name': rec.parent_name
            })

    def generate_report(self): # ექსელ ფაილის გენერირება
        output = BytesIO()  #  შედეგი გამოაქვს ბაიტის სახით
        book = Workbook(output)  # ქმნის ექსელის ფანჯარას, სადაც წერს აუთფუთში მოცემულ მონაცემს
        sheet = book.add_worksheet('Student Information')  # book-ს ამატებს ახალ worksheet-ს სათაურით "Student Information"
        sheet.set_column('A:AZ', 15.0)  # აყენებს A-დან AZ-მდე სვეტების სიგანეს 18.0-მდე
        sheet.set_row(0, 60) # ეს ფუნქცია გამოიყენება მწკრივის სიმაღლის დასაყენებლად. პირველი პარამეტრი 0 განსაზღვრავს იმ მწკრივის ინდექსს, რომლის შეცვლაც გსურთ, მეორე პარამეტრი 60 განსაზღვრავს მწკრივის სიმაღლეს. ამ შემთხვევაში, ის დაყენებულია 60 პიქსელზე.
        sheet.freeze_panes(1, 0)  # აფიქსირებს პირველ რიგს და მარცხენა სვეტს (სტრიქონი 1, სვეტი 0). ეს ნიშნავს, რომ სამუშაო ფურცლის სქროლვისას, დაფიქსირებული რიგები და სვეტები ხილული დარჩება.
        header_style = book.add_format(
            {'font_size': 10, 'bold': True, 'font_color': '#081F3E', 'align': 'center',
             'border': 1, 'border_color': '#0D0D0D', 'fg_color': '#D7E4BC',
             'valign': 'center'})   # სათაურისთვის ქმნის ფორმატს ახალი თვისებებით
        header_style.set_text_wrap()
        header_names = ['სტუდენტის სახელი',
                        'გვარი',
                        'პირადი ნომერი',
                        'დაბადების თარიღი',
                        'მშობლის მობილურის ნომერი',
                        'მისამართი',
                        'სიის ნომერი',
                        'შეფასება',
                        ]

        for i, name in enumerate(header_names):
            sheet.write(0, i, name, header_style) # 0 row, i არის სვეტები, name არის სვეტის სათაური,header_style არის ჰედერის სტილი

        query = f"""
        SELECT
        name,  -- 'სტუდენტის სახელი, გვარი',
        last_name,  -- 'სტუდენტის სახელი, გვარი',
        id_number,  -- 'პირადი ნომერი',
        birth_date, --'დაბადების თარიღი',
        mobile,     -- 'მშობლის მობილურის ნომერი',
        address,   --'მისამართი',
        roll_number,   --'სიის ნომერი',
        grade_student --'შეფასება',

        FROM res_partner
        where id = {self.id}
        """                     # Sql-ის სელექთით ამოაქვს ინფორმაცია res.partner-დან, where id -ით ვუთითებ კონკრეტულ ერთეულს

        self.env.cr.execute(query)  # უშვებს სელექთს
        rowcount = 1  #
        for rec in self.env.cr.fetchall(): # fetchall-ს გამოაქვს ყველა ინფორმაცია სელექთიდან
            sheet.write_row(rowcount, 0, rec)
            rowcount += 1

        book.close()
        output.seek(0)
        excel_file = base64.b64encode(output.getvalue())
        return {
            'excel_file': excel_file,
            'filename': f'{self.name}_{self.last_name}.xlsx',
        }

    def report(self):

        results = self.generate_report()


        attachment = self.env['ir.attachment'].create({   # attachment ფაილის შექმნა
            'datas': results.get('excel_file'),
            'name': results.get('filename'),
            'mimetype': 'application/vnd.ms-excel'
        })

        self.write({
                    'files':  [(6,0,[ attachment.id])],
                    })


class SearchStudent(models.Model):
    _name = 'search.student'

    student_roll_number = fields.Integer(string='სიის ნომერი')

    student_list = fields.Many2many('student.information')

    def studentsearch(self):
        students = self.env['student.information'].search([('roll_number_student', '=', self.student_roll_number)]).ids

        self.update({
            'student_list': [(6, 0, students)]
        })
