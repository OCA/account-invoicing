from setuptools import setup

setup(
    name="odoo-addon-account_manual_currency",
    version="16.0.1.0.1",
    license="LGPL-3",
    author="Odoo Community Association (OCA)",
    install_requires=["odoo>=16.0,<17.0"],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Odoo",
    ],
    include_package_data=True,
    zip_safe=False,
    odoo_addon=True,
)

