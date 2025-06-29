import setuptools

setuptools.setup(
    name="odoo-addon-account_manual_currency",
    version="16.0.1.0.1",
    license="LGPL-3",
    author="Odoo Community Association (OCA)",
    install_requires=["odoo>=16.0,<17.0"],
    include_package_data=True,
    zip_safe=False,
    odoo_addon=True,
)
