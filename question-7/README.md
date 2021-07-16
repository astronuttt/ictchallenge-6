#  HDWallet
اچ دی ولت ها به ما کمک میکنند تا با یک
mnemonic ( seed )
نامحدود پابلیک آدرس بسازیم
یک درخت برای آدرس ها ساخته میشه و شما میتونید همه مقادیر رو sweep کنید
و... 
[BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)


# راه حل؟
درواقع راه حل درست برای ساخت پیمنت برای هر کاربر و جلوگیری از تقلب استفاده از اچ دی ولت بجای یک پابلیک آدرس ثابت هست.
در این روش کاربر در سایت درخواست فروش مثلا بیتکوین به صرافی رو میده, مقدار رو تعیین میکنه و تایید میکنه. صرافی برای کاربر یک پابلیک آدرس میسازه. توی دیتابیس مقدار بیتکوین و اطلاعات کاربر رو ذخیره میکنه و ازش میخواد که به میزان مشخص به آدرس مربوطه بیت کوین واریز کنه.
این آدرس مخصوص همون کاربر و همون پیمنت هست و میتوان با اطلاعات ثبت شده برای اون آدرس در دیتابیس اعتبار سنجی کرد
کاربر بعد از پرداخت وارد سایت میشه برای تایید تراکنش
دیگه نیازی به ترنزاکشن آیدی هم نیست. صرافی میتونه با بررسی بالانس آدرس ساخته شده برای کاربر و تطابق دادن آن با مقدار پیمنت تراکنش رو تایید کنه.

# یک راه حل دیگر...
بعضی از صرافی ها برای هر کاربر یک ولت (پرایوت کی) در هنگام رجیستر میسازند و در تراکنش ها از اون استفاده میکنند. در این صورت آدرسی که به هر کاربر داده میشه مربوط به ولت کاربر هست و از اونجایی که پرایوت کی ولت در دست صرافی هست میتواند مقادیر داخل آن را مدیریت کند.

روش اول بهتر است. ریسک ذخیره کردن پرایوت کی ها در دیتابیس و هزینه (fee) انتقال مقادیر از ولت کاربر به ولت اصلی صرافی و ... مشکلات این روش هست.


# نمونه کد اچ دی ولت در پایتون
```python
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Levels, \
    Bip44Changes

class Bip44Wallet(object):
    def __init__(self, mnemonic: str, coin_type: Bip44Coins):
        SEED_BYTES = Bip39SeedGenerator(mnemonic).Generate()

        bip_obj = Bip44.FromSeed(SEED_BYTES, coin_type)
        if bip_obj.IsLevel(Bip44Levels.MASTER):
            bip_obj = bip_obj.Purpose()
        if bip_obj.IsLevel(Bip44Levels.PURPOSE):
            bip_obj = bip_obj.Coin()
        if bip_obj.IsLevel(Bip44Levels.COIN):
            bip_obj = bip_obj.Account(0)
        if bip_obj.IsLevel(Bip44Levels.ACCOUNT):
            bip_obj = bip_obj.Change(Bip44Changes.CHAIN_EXT)

        assert bip_obj.IsLevel(Bip44Levels.CHANGE)
        self._bip_obj = bip_obj

    def get_address(self, address_id=0):
        return self._bip_obj.AddressIndex(address_id).PublicKey().ToAddress()
```

