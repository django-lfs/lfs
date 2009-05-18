
from south.db import db
from django.db import models
from lfs.catalog.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'ProductPropertyValue'
        db.create_table('catalog_productpropertyvalue', (
            ('product', models.ForeignKey(orm.Product, related_name="property_values", verbose_name=_(u"Product"))),
            ('property', models.ForeignKey(orm.Property, related_name="property_values", verbose_name=_(u"Property"))),
            ('value', models.CharField(max_length=100, blank=True)),
            ('parent_id', models.IntegerField(null=True, blank=True)),
            ('value_as_float', models.FloatField(null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('catalog', ['ProductPropertyValue'])
        
        # Adding model 'StaticBlock'
        db.create_table('catalog_staticblock', (
            ('html', models.TextField(_(u"HTML"), blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_(u"Name"), max_length=30)),
        ))
        db.send_create_signal('catalog', ['StaticBlock'])
        
        # Adding model 'PropertyGroup'
        db.create_table('catalog_propertygroup', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=50, blank=True)),
        ))
        db.send_create_signal('catalog', ['PropertyGroup'])
        
        # Adding model 'Category'
        db.create_table('catalog_category', (
            ('static_block', models.ForeignKey(orm.StaticBlock, related_name="categories", null=True, verbose_name=_(u"Static block"), blank=True)),
            ('meta_description', models.TextField(_(u"Meta description"), blank=True)),
            ('show_all_products', models.BooleanField(_(u"Show all products"), default=True)),
            ('name', models.CharField(_(u"Name"), max_length=50)),
            ('parent', models.ForeignKey(orm.Category, null=True, verbose_name=_(u"Parent"), blank=True)),
            ('image', ImageWithThumbsField(_(u"Image"), null=True, upload_to="images", sizes=((60,60),(100,100),(200,200),(400,400)), blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('content', models.IntegerField(_(u"Content"), default=CONTENT_PRODUCTS)),
            ('active_formats', models.BooleanField(_(u"Active formats"), default=False)),
            ('meta_keywords', models.TextField(_(u"Meta keywords"), blank=True)),
            ('product_cols', models.IntegerField(_(u"Product cols"), default=3)),
            ('category_cols', models.IntegerField(_(u"Category cols"), default=3)),
            ('short_description', models.TextField(_(u"Short description"), blank=True)),
            ('position', models.IntegerField(_(u"Position"), default=1000)),
            ('product_rows', models.IntegerField(_(u"Product rows"), default=3)),
            ('slug', models.SlugField(_(u"Slug"), unique=True)),
            ('description', models.TextField(_(u"Description"), blank=True)),
        ))
        db.send_create_signal('catalog', ['Category'])
        
        # Adding model 'ProductAccessories'
        db.create_table('catalog_productaccessories', (
            ('position', models.IntegerField(_(u"Position"), default=999)),
            ('product', models.ForeignKey(orm.Product, related_name="productaccessories_product", verbose_name=_(u"Product"))),
            ('quantity', models.FloatField(_(u"Quantity"), default=1)),
            ('id', models.AutoField(primary_key=True)),
            ('accessory', models.ForeignKey(orm.Product, related_name="productaccessories_accessory", verbose_name=_(u"Acessory"))),
        ))
        db.send_create_signal('catalog', ['ProductAccessories'])
        
        # Adding model 'FilterStep'
        db.create_table('catalog_filterstep', (
            ('start', models.FloatField()),
            ('property', models.ForeignKey(orm.Property, related_name="steps", verbose_name=_(u"Property"))),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('catalog', ['FilterStep'])
        
        # Adding model 'Product'
        db.create_table('catalog_product', (
            ('effective_price', models.FloatField(_(u"Price"), blank=True)),
            ('meta_keywords', models.TextField(_(u"Meta keywords"), blank=True)),
            ('weight', models.FloatField(_(u"Weight"), default=0.0)),
            ('tax', models.ForeignKey(orm['tax.Tax'], null=True, verbose_name=_(u"Tax"), blank=True)),
            ('active_meta_keywords', models.BooleanField(_(u"Active meta keywords"), default=False)),
            ('creation_date', models.DateTimeField(_(u"Creation date"), auto_now_add=True)),
            ('parent', models.ForeignKey(orm.Product, related_name="variants", null=True, verbose_name=_(u"Parent"), blank=True)),
            ('active_accessories', models.BooleanField(_(u"Active accessories"), default=False)),
            ('id', models.AutoField(primary_key=True)),
            ('sku', models.CharField(_(u"SKU"), max_length=30, blank=True)),
            ('active_price', models.BooleanField(_(u"Active Price"), default=True)),
            ('manage_stock_amount', models.BooleanField(_(u"Manage stock amount"), default=True)),
            ('sub_type', models.CharField(_(u"Subtype"), default=STANDARD_PRODUCT, max_length=10)),
            ('width', models.FloatField(_(u"Width"), default=0.0)),
            ('short_description', models.TextField(_(u"Short description"), blank=True)),
            ('meta_description', models.TextField(_(u"Meta description"), blank=True)),
            ('active_description', models.BooleanField(_(u"Active description"), default=False)),
            ('description', models.TextField(_(u"Description"), blank=True)),
            ('order_time', models.ForeignKey(orm.DeliveryTime, related_name="products_order_time", null=True, verbose_name=_(u"Order time"), blank=True)),
            ('price', models.FloatField(_(u"Price"), default=0.0)),
            ('manual_delivery_time', models.BooleanField(_(u"Manual delivery time"), default=False)),
            ('stock_amount', models.DecimalField(_(u"Stock amount"), default=0, max_digits=3, decimal_places=1)),
            ('default_variant', models.ForeignKey(orm.Product, null=True, verbose_name=_(u"Default variant"), blank=True)),
            ('ordered_at', models.DateField(_(u"Ordered at"), null=True, blank=True)),
            ('active', models.BooleanField(_(u"Active"), default=False)),
            ('variants_display_type', models.IntegerField(_(u"Variants display type"), default=LIST)),
            ('height', models.FloatField(_(u"Height"), default=0.0)),
            ('slug', models.SlugField(_(u"Slug"), max_length=80, unique=True)),
            ('delivery_time', models.ForeignKey(orm.DeliveryTime, related_name="products_delivery_time", null=True, verbose_name=_(u"Delivery time"), blank=True)),
            ('active_sku', models.BooleanField(_(u"Active SKU"), default=True)),
            ('name', models.CharField(_(u"Name"), max_length=80)),
            ('active_images', models.BooleanField(_(u"Active Images"), default=False)),
            ('for_sale_price', models.FloatField(_(u"For sale price"), default=0.0)),
            ('active_meta_description', models.BooleanField(_(u"Active meta description"), default=False)),
            ('active_name', models.BooleanField(_(u"Active name"), default=True)),
            ('deliverable', models.BooleanField(_(u"Deliverable"), default=True)),
            ('for_sale', models.BooleanField(_(u"For sale"), default=False)),
            ('length', models.FloatField(_(u"Length"), default=0.0)),
            ('active_related_products', models.BooleanField(_(u"Active related products"), default=False)),
            ('active_short_description', models.BooleanField(_(u"Active short description"), default=False)),
        ))
        db.send_create_signal('catalog', ['Product'])
        
        # Adding model 'DeliveryTime'
        db.create_table('catalog_deliverytime', (
            ('max', models.FloatField(_(u"Max"))),
            ('description', models.TextField(_(u"Description"), blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('unit', models.PositiveSmallIntegerField(_(u"Unit"), default=DELIVERY_TIME_UNIT_DAYS)),
            ('min', models.FloatField(_(u"Min"))),
        ))
        db.send_create_signal('catalog', ['DeliveryTime'])
        
        # Adding model 'PropertyOption'
        db.create_table('catalog_propertyoption', (
            ('position', models.IntegerField(_(u"Position"), default=99)),
            ('price', models.FloatField(_(u"Price"), default=0.0, null=True, blank=True)),
            ('property', models.ForeignKey(orm.Property, related_name="options", verbose_name=_(u"Property"))),
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_(u"Name"), max_length=30)),
        ))
        db.send_create_signal('catalog', ['PropertyOption'])
        
        # Adding model 'ProductsPropertiesRelation'
        db.create_table('catalog_productspropertiesrelation', (
            ('position', models.IntegerField(_(u"Position"), default=999)),
            ('product', models.ForeignKey(orm.Product, related_name="productsproperties", verbose_name=_(u"Product"))),
            ('property', models.ForeignKey(orm.Property, verbose_name=_(u"Property"))),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('catalog', ['ProductsPropertiesRelation'])
        
        # Adding model 'Image'
        db.create_table('catalog_image', (
            ('title', models.CharField(_(u"Title"), max_length=100, blank=True)),
            ('image', ImageWithThumbsField(_(u"Image"), null=True, upload_to="images", sizes=((60,60),(100,100),(200,200),(400,400)), blank=True)),
            ('content_type', models.ForeignKey(orm['contenttypes.ContentType'], related_name="image", null=True, verbose_name=_(u"Content type"), blank=True)),
            ('position', models.PositiveSmallIntegerField(_(u"Position"), default=999)),
            ('content_id', models.PositiveIntegerField(_(u"Content id"), null=True, blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('catalog', ['Image'])
        
        # Adding model 'GroupsPropertiesRelation'
        db.create_table('catalog_groupspropertiesrelation', (
            ('position', models.IntegerField(_(u"Position"), default=999)),
            ('property', models.ForeignKey(orm.Property, verbose_name=_(u"Property"))),
            ('group', models.ForeignKey(orm.PropertyGroup, related_name="groupproperties", verbose_name=_(u"Group"))),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('catalog', ['GroupsPropertiesRelation'])
        
        # Adding model 'Property'
        db.create_table('catalog_property', (
            ('name', models.CharField(_(u"Name"), max_length=50)),
            ('filterable', models.BooleanField(default=True)),
            ('type', models.PositiveSmallIntegerField(_(u"Type"), default=PROPERTY_TEXT_FIELD)),
            ('display_on_product', models.BooleanField(_(u"Display on product"), default=True)),
            ('step', models.IntegerField(_(u"Step"), null=True, blank=True)),
            ('step_type', models.PositiveSmallIntegerField(_(u"Step type"), default=PROPERTY_STEP_TYPE_AUTOMATIC)),
            ('position', models.IntegerField(_(u"Position"), null=True, blank=True)),
            ('local', models.BooleanField(default=False)),
            ('id', models.AutoField(primary_key=True)),
            ('unit', models.CharField(_(u"Unit"), max_length=15, blank=True)),
            ('display_no_results', models.BooleanField(_(u"Display no results"), default=False)),
        ))
        db.send_create_signal('catalog', ['Property'])
        
        # Adding ManyToManyField 'Product.related_products'
        db.create_table('catalog_product_related_products', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_product', models.ForeignKey(Product, null=False)),
            ('to_product', models.ForeignKey(Product, null=False))
        ))
        
        # Adding ManyToManyField 'PropertyGroup.products'
        db.create_table('catalog_propertygroup_products', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('propertygroup', models.ForeignKey(PropertyGroup, null=False)),
            ('product', models.ForeignKey(Product, null=False))
        ))
        
        # Adding ManyToManyField 'Category.products'
        db.create_table('catalog_category_products', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(Category, null=False)),
            ('product', models.ForeignKey(Product, null=False))
        ))
        
        # Creating unique_together for [product, property] on ProductsPropertiesRelation.
        db.create_unique('catalog_productspropertiesrelation', ['product_id', 'property_id'])
        
        # Creating unique_together for [product, property, value] on ProductPropertyValue.
        db.create_unique('catalog_productpropertyvalue', ['product_id', 'property_id', 'value'])
        
        # Creating unique_together for [group, property] on GroupsPropertiesRelation.
        db.create_unique('catalog_groupspropertiesrelation', ['group_id', 'property_id'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'ProductPropertyValue'
        db.delete_table('catalog_productpropertyvalue')
        
        # Deleting model 'StaticBlock'
        db.delete_table('catalog_staticblock')
        
        # Deleting model 'PropertyGroup'
        db.delete_table('catalog_propertygroup')
        
        # Deleting model 'Category'
        db.delete_table('catalog_category')
        
        # Deleting model 'ProductAccessories'
        db.delete_table('catalog_productaccessories')
        
        # Deleting model 'FilterStep'
        db.delete_table('catalog_filterstep')
        
        # Deleting model 'Product'
        db.delete_table('catalog_product')
        
        # Deleting model 'DeliveryTime'
        db.delete_table('catalog_deliverytime')
        
        # Deleting model 'PropertyOption'
        db.delete_table('catalog_propertyoption')
        
        # Deleting model 'ProductsPropertiesRelation'
        db.delete_table('catalog_productspropertiesrelation')
        
        # Deleting model 'Image'
        db.delete_table('catalog_image')
        
        # Deleting model 'GroupsPropertiesRelation'
        db.delete_table('catalog_groupspropertiesrelation')
        
        # Deleting model 'Property'
        db.delete_table('catalog_property')
        
        # Dropping ManyToManyField 'Product.related_products'
        db.delete_table('catalog_product_related_products')
        
        # Dropping ManyToManyField 'PropertyGroup.products'
        db.delete_table('catalog_propertygroup_products')
        
        # Dropping ManyToManyField 'Category.products'
        db.delete_table('catalog_category_products')
        
        # Deleting unique_together for [product, property] on ProductsPropertiesRelation.
        db.delete_unique('catalog_productspropertiesrelation', ['product_id', 'property_id'])
        
        # Deleting unique_together for [product, property, value] on ProductPropertyValue.
        db.delete_unique('catalog_productpropertyvalue', ['product_id', 'property_id', 'value'])
        
        # Deleting unique_together for [group, property] on GroupsPropertiesRelation.
        db.delete_unique('catalog_groupspropertiesrelation', ['group_id', 'property_id'])
        
    
    
    models = {
        'catalog.productpropertyvalue': {
            'Meta': {'unique_together': '("product","property","value")'},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'parent_id': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'product': ('models.ForeignKey', ['Product'], {'related_name': '"property_values"', 'verbose_name': '_(u"Product")'}),
            'property': ('models.ForeignKey', ['"Property"'], {'related_name': '"property_values"', 'verbose_name': '_(u"Property")'}),
            'value': ('models.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'value_as_float': ('models.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'catalog.staticblock': {
            'html': ('models.TextField', ['_(u"HTML")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '30'})
        },
        'catalog.propertygroup': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'products': ('models.ManyToManyField', ['Product'], {'related_name': '"property_groups"', 'verbose_name': '_(u"Products")'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'catalog.category': {
            'Meta': {'ordering': '("position",)'},
            'active_formats': ('models.BooleanField', ['_(u"Active formats")'], {'default': 'False'}),
            'category_cols': ('models.IntegerField', ['_(u"Category cols")'], {'default': '3'}),
            'content': ('models.IntegerField', ['_(u"Content")'], {'default': 'CONTENT_PRODUCTS'}),
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('ImageWithThumbsField', ['_(u"Image")'], {'null': 'True', 'upload_to': '"images"', 'sizes': '((60,60),(100,100),(200,200),(400,400))', 'blank': 'True'}),
            'meta_description': ('models.TextField', ['_(u"Meta description")'], {'blank': 'True'}),
            'meta_keywords': ('models.TextField', ['_(u"Meta keywords")'], {'blank': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '50'}),
            'parent': ('models.ForeignKey', ['"self"'], {'null': 'True', 'verbose_name': '_(u"Parent")', 'blank': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '1000'}),
            'product_cols': ('models.IntegerField', ['_(u"Product cols")'], {'default': '3'}),
            'product_rows': ('models.IntegerField', ['_(u"Product rows")'], {'default': '3'}),
            'products': ('models.ManyToManyField', ['"Product"'], {'related_name': '"categories"', 'verbose_name': '_(u"Products")', 'blank': 'True'}),
            'short_description': ('models.TextField', ['_(u"Short description")'], {'blank': 'True'}),
            'show_all_products': ('models.BooleanField', ['_(u"Show all products")'], {'default': 'True'}),
            'slug': ('models.SlugField', ['_(u"Slug")'], {'unique': 'True'}),
            'static_block': ('models.ForeignKey', ['"StaticBlock"'], {'related_name': '"categories"', 'null': 'True', 'verbose_name': '_(u"Static block")', 'blank': 'True'})
        },
        'catalog.productaccessories': {
            'Meta': {'ordering': '("position",)'},
            'accessory': ('models.ForeignKey', ['"Product"'], {'related_name': '"productaccessories_accessory"', 'verbose_name': '_(u"Acessory")'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '999'}),
            'product': ('models.ForeignKey', ['"Product"'], {'related_name': '"productaccessories_product"', 'verbose_name': '_(u"Product")'}),
            'quantity': ('models.FloatField', ['_(u"Quantity")'], {'default': '1'})
        },
        'catalog.filterstep': {
            'Meta': {'ordering': '["start"]'},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'property': ('models.ForeignKey', ['Property'], {'related_name': '"steps"', 'verbose_name': '_(u"Property")'}),
            'start': ('models.FloatField', [], {})
        },
        'catalog.product': {
            'Meta': {'ordering': '("name",)'},
            'accessories': ('models.ManyToManyField', ['"Product"'], {'related_name': '"reverse_accessories"', 'through': '"ProductAccessories"', 'blank': 'True', 'symmetrical': 'False', 'null': 'True', 'verbose_name': '_(u"Acessories")'}),
            'active': ('models.BooleanField', ['_(u"Active")'], {'default': 'False'}),
            'active_accessories': ('models.BooleanField', ['_(u"Active accessories")'], {'default': 'False'}),
            'active_description': ('models.BooleanField', ['_(u"Active description")'], {'default': 'False'}),
            'active_images': ('models.BooleanField', ['_(u"Active Images")'], {'default': 'False'}),
            'active_meta_description': ('models.BooleanField', ['_(u"Active meta description")'], {'default': 'False'}),
            'active_meta_keywords': ('models.BooleanField', ['_(u"Active meta keywords")'], {'default': 'False'}),
            'active_name': ('models.BooleanField', ['_(u"Active name")'], {'default': 'True'}),
            'active_price': ('models.BooleanField', ['_(u"Active Price")'], {'default': 'True'}),
            'active_related_products': ('models.BooleanField', ['_(u"Active related products")'], {'default': 'False'}),
            'active_short_description': ('models.BooleanField', ['_(u"Active short description")'], {'default': 'False'}),
            'active_sku': ('models.BooleanField', ['_(u"Active SKU")'], {'default': 'True'}),
            'creation_date': ('models.DateTimeField', ['_(u"Creation date")'], {'auto_now_add': 'True'}),
            'default_variant': ('models.ForeignKey', ['"self"'], {'null': 'True', 'verbose_name': '_(u"Default variant")', 'blank': 'True'}),
            'deliverable': ('models.BooleanField', ['_(u"Deliverable")'], {'default': 'True'}),
            'delivery_time': ('models.ForeignKey', ['"DeliveryTime"'], {'related_name': '"products_delivery_time"', 'null': 'True', 'verbose_name': '_(u"Delivery time")', 'blank': 'True'}),
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'effective_price': ('models.FloatField', ['_(u"Price")'], {'blank': 'True'}),
            'for_sale': ('models.BooleanField', ['_(u"For sale")'], {'default': 'False'}),
            'for_sale_price': ('models.FloatField', ['_(u"For sale price")'], {'default': '0.0'}),
            'height': ('models.FloatField', ['_(u"Height")'], {'default': '0.0'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'images': ('generic.GenericRelation', ['"Image"'], {'object_id_field': '"content_id"', 'verbose_name': '_(u"Images")', 'content_type_field': '"content_type"'}),
            'length': ('models.FloatField', ['_(u"Length")'], {'default': '0.0'}),
            'manage_stock_amount': ('models.BooleanField', ['_(u"Manage stock amount")'], {'default': 'True'}),
            'manual_delivery_time': ('models.BooleanField', ['_(u"Manual delivery time")'], {'default': 'False'}),
            'meta_description': ('models.TextField', ['_(u"Meta description")'], {'blank': 'True'}),
            'meta_keywords': ('models.TextField', ['_(u"Meta keywords")'], {'blank': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '80'}),
            'order_time': ('models.ForeignKey', ['"DeliveryTime"'], {'related_name': '"products_order_time"', 'null': 'True', 'verbose_name': '_(u"Order time")', 'blank': 'True'}),
            'ordered_at': ('models.DateField', ['_(u"Ordered at")'], {'null': 'True', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ['"self"'], {'related_name': '"variants"', 'null': 'True', 'verbose_name': '_(u"Parent")', 'blank': 'True'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0'}),
            'related_products': ('models.ManyToManyField', ['"self"'], {'related_name': '"reverse_related_products"', 'symmetrical': 'False', 'null': 'True', 'verbose_name': '_(u"Related products")', 'blank': 'True'}),
            'short_description': ('models.TextField', ['_(u"Short description")'], {'blank': 'True'}),
            'sku': ('models.CharField', ['_(u"SKU")'], {'max_length': '30', 'blank': 'True'}),
            'slug': ('models.SlugField', ['_(u"Slug")'], {'max_length': '80', 'unique': 'True'}),
            'stock_amount': ('models.DecimalField', ['_(u"Stock amount")'], {'default': '0', 'max_digits': '3', 'decimal_places': '1'}),
            'sub_type': ('models.CharField', ['_(u"Subtype")'], {'default': 'STANDARD_PRODUCT', 'max_length': '10'}),
            'tax': ('models.ForeignKey', ['Tax'], {'null': 'True', 'verbose_name': '_(u"Tax")', 'blank': 'True'}),
            'variants_display_type': ('models.IntegerField', ['_(u"Variants display type")'], {'default': 'LIST'}),
            'weight': ('models.FloatField', ['_(u"Weight")'], {'default': '0.0'}),
            'width': ('models.FloatField', ['_(u"Width")'], {'default': '0.0'})
        },
        'catalog.deliverytime': {
            'Meta': {'ordering': '("min",)'},
            'description': ('models.TextField', ['_(u"Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'max': ('models.FloatField', ['_(u"Max")'], {}),
            'min': ('models.FloatField', ['_(u"Min")'], {}),
            'unit': ('models.PositiveSmallIntegerField', ['_(u"Unit")'], {'default': 'DELIVERY_TIME_UNIT_DAYS'})
        },
        'catalog.propertyoption': {
            'Meta': {'ordering': '["position"]'},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '30'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '99'}),
            'price': ('models.FloatField', ['_(u"Price")'], {'default': '0.0', 'null': 'True', 'blank': 'True'}),
            'property': ('models.ForeignKey', ['Property'], {'related_name': '"options"', 'verbose_name': '_(u"Property")'})
        },
        'catalog.productspropertiesrelation': {
            'Meta': {'ordering': '("position",)', 'unique_together': '("product","property")'},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '999'}),
            'product': ('models.ForeignKey', ['Product'], {'related_name': '"productsproperties"', 'verbose_name': '_(u"Product")'}),
            'property': ('models.ForeignKey', ['Property'], {'verbose_name': '_(u"Property")'})
        },
        'catalog.image': {
            'Meta': {'ordering': '("position",)'},
            'content_id': ('models.PositiveIntegerField', ['_(u"Content id")'], {'null': 'True', 'blank': 'True'}),
            'content_type': ('models.ForeignKey', ['ContentType'], {'related_name': '"image"', 'null': 'True', 'verbose_name': '_(u"Content type")', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('ImageWithThumbsField', ['_(u"Image")'], {'null': 'True', 'upload_to': '"images"', 'sizes': '((60,60),(100,100),(200,200),(400,400))', 'blank': 'True'}),
            'position': ('models.PositiveSmallIntegerField', ['_(u"Position")'], {'default': '999'}),
            'title': ('models.CharField', ['_(u"Title")'], {'max_length': '100', 'blank': 'True'})
        },
        'catalog.groupspropertiesrelation': {
            'Meta': {'ordering': '("position",)', 'unique_together': '("group","property")'},
            'group': ('models.ForeignKey', ['PropertyGroup'], {'related_name': '"groupproperties"', 'verbose_name': '_(u"Group")'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'default': '999'}),
            'property': ('models.ForeignKey', ['Property'], {'verbose_name': '_(u"Property")'})
        },
        'tax.tax': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'catalog.property': {
            'Meta': {'ordering': '["position"]'},
            'display_no_results': ('models.BooleanField', ['_(u"Display no results")'], {'default': 'False'}),
            'display_on_product': ('models.BooleanField', ['_(u"Display on product")'], {'default': 'True'}),
            'filterable': ('models.BooleanField', [], {'default': 'True'}),
            'groups': ('models.ManyToManyField', ['PropertyGroup'], {'related_name': '"properties"', 'through': '"GroupsPropertiesRelation"', 'null': 'True', 'verbose_name': '_(u"Group")', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'local': ('models.BooleanField', [], {'default': 'False'}),
            'name': ('models.CharField', ['_(u"Name")'], {'max_length': '50'}),
            'position': ('models.IntegerField', ['_(u"Position")'], {'null': 'True', 'blank': 'True'}),
            'products': ('models.ManyToManyField', ['Product'], {'related_name': '"properties"', 'through': '"ProductsPropertiesRelation"', 'null': 'True', 'verbose_name': '_(u"Products")', 'blank': 'True'}),
            'step': ('models.IntegerField', ['_(u"Step")'], {'null': 'True', 'blank': 'True'}),
            'step_type': ('models.PositiveSmallIntegerField', ['_(u"Step type")'], {'default': 'PROPERTY_STEP_TYPE_AUTOMATIC'}),
            'type': ('models.PositiveSmallIntegerField', ['_(u"Type")'], {'default': 'PROPERTY_TEXT_FIELD'}),
            'unit': ('models.CharField', ['_(u"Unit")'], {'max_length': '15', 'blank': 'True'})
        }
    }
    
    complete_apps = ['catalog']
