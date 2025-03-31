from io import BytesIO
import discord
from discord.ext import commands
import dotenv
import requests
from PIL import Image

import re
import os
from collections import Counter
import xml.etree.ElementTree as ET

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") or ''
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL") or '')

FRONT_SHIRT_COORDS = (231, 74, 359, 202)
BACK_SHIRT_COORDS = (427, 74, 555, 202)
FRONT_RIGHT_ARM_COORDS = (217, 355, 281, 483)
FRONT_LEFT_ARM_COORDS = (308, 355, 372, 483)
BACK_RIGHT_ARM_COORDS = (85, 355, 149, 483)
BACK_LEFT_ARM_COORDS = (440, 355, 504, 483)
RIGHT_ARM_COORDS = (151, 355, 215, 483)
LEFT_ARM_COORDS = (374, 355, 438, 483)

FRONT_RIGHT_LEG_COORDS = (217, 355, 281, 483)
FRONT_LEFT_LEG_COORDS = (308, 355, 372, 483)
BACK_RIGHT_LEG_COORDS = (85, 355, 149, 483)
BACK_LEFT_LEG_COORDS = (440, 355, 504, 483)
RIGHT_LEG_COORDS = (151, 355, 215, 483)
LEFT_LEG_COORDS = (374, 355, 438, 483)

TEMPLATE_FRONT_SHIRT_COORDS = (168, 69)
TEMPLATE_BACK_SHIRT_COORDS = (453, 69)
TEMPLATE_FRONT_RIGHT_ARM_COORDS = (104, 69)
TEMPLATE_FRONT_LEFT_ARM_COORDS = (296, 69)
TEMPLATE_BACK_RIGHT_ARM_COORDS = (581, 69)
TEMPALTE_BACK_LEFT_ARM_COORDS = (389, 69)
TEMPLATE_RIGHT_ARM_COORDS = (25, 69)
TEMPLATE_LEFT_ARM_COORDS = (660, 69)

TEMPLATE_FRONT_RIGHT_LEG_COORDS = (168, 197)
TEMPLATE_FRONT_LEFT_LEG_COORDS = (232, 197)
TEMPLATE_BACK_RIGHT_LEG_COORDS = (517, 197)
TEMPLATE_BACK_LEFT_LEG_COORDS = (453, 197)
TEMPLATE_RIGHT_LEG_COORDS = (25, 197)
TEMPLATE_LEFT_LEG_COORDS = (660, 197)

PROCESSING_EMBED = discord.Embed(
    title='Processing...',
    description='Please wait while we process your request',
    color=discord.Color.blurple()
)

bot = discord.Bot()

@bot.event
async def on_ready():
    if bot.user:
        print(f'Logged in as {bot.user.name} - {bot.user.id}')


def place_shirt(template, shirt):
    shirt = shirt.convert('RGBA')

    front_shirt = shirt.crop(FRONT_SHIRT_COORDS)
    back_shirt = shirt.crop(BACK_SHIRT_COORDS)
    front_right_arm = shirt.crop(FRONT_RIGHT_ARM_COORDS)
    front_left_arm = shirt.crop(FRONT_LEFT_ARM_COORDS)
    back_right_arm = shirt.crop(BACK_RIGHT_ARM_COORDS)
    back_left_arm = shirt.crop(BACK_LEFT_ARM_COORDS)
    right_arm = shirt.crop(RIGHT_ARM_COORDS)
    left_arm = shirt.crop(LEFT_ARM_COORDS)

    template.paste(front_shirt, TEMPLATE_FRONT_SHIRT_COORDS, front_shirt)
    template.paste(back_shirt, TEMPLATE_BACK_SHIRT_COORDS, back_shirt)
    template.paste(front_right_arm, TEMPLATE_FRONT_RIGHT_ARM_COORDS, front_right_arm)
    template.paste(front_left_arm, TEMPLATE_FRONT_LEFT_ARM_COORDS, front_left_arm)
    template.paste(back_right_arm, TEMPLATE_BACK_RIGHT_ARM_COORDS, back_right_arm)
    template.paste(back_left_arm, TEMPALTE_BACK_LEFT_ARM_COORDS, back_left_arm)
    template.paste(right_arm, TEMPLATE_RIGHT_ARM_COORDS, right_arm)
    template.paste(left_arm, TEMPLATE_LEFT_ARM_COORDS, left_arm)

    shirt_data = list(front_shirt.getdata())
    shirt_colors = Counter(shirt_data)

    most_common = shirt_colors.most_common(1)[0][0]

    return most_common


def place_pants(template, pants):
    pants = pants.convert('RGBA')

    front_right_leg = pants.crop(FRONT_RIGHT_LEG_COORDS)
    front_left_leg = pants.crop(FRONT_LEFT_LEG_COORDS)
    back_right_leg = pants.crop(BACK_RIGHT_LEG_COORDS)
    back_left_leg = pants.crop(BACK_LEFT_LEG_COORDS)
    right_leg = pants.crop(RIGHT_LEG_COORDS)
    left_leg = pants.crop(LEFT_LEG_COORDS)

    template.paste(front_right_leg, TEMPLATE_FRONT_RIGHT_LEG_COORDS, front_right_leg)
    template.paste(front_left_leg, TEMPLATE_FRONT_LEFT_LEG_COORDS, front_left_leg)
    template.paste(back_right_leg, TEMPLATE_BACK_RIGHT_LEG_COORDS, back_right_leg)
    template.paste(back_left_leg, TEMPLATE_BACK_LEFT_LEG_COORDS, back_left_leg)
    template.paste(right_leg, TEMPLATE_RIGHT_LEG_COORDS, right_leg)
    template.paste(left_leg, TEMPLATE_LEFT_LEG_COORDS, left_leg)

    pants_data = list(front_right_leg.getdata())
    pants_colors = Counter(pants_data)

    most_common = pants_colors.most_common(1)[0][0]

    return most_common


@bot.slash_command(name='showcase')
async def showcase(
    ctx,
    shirt: discord.Option(discord.SlashCommandOptionType.attachment, 'The shirt to showcase', required=False),  # pyright: ignore
    pants: discord.Option(discord.SlashCommandOptionType.attachment, 'The pants to showcase', required=False),  # pyright: ignore
):
    await ctx.defer()

    if not shirt and not pants:
        return await ctx.respond('You must provide a shirt or pants to showcase', ephemeral=True)

    if shirt and (shirt.width != 585 and shirt.height != 559):
        return await ctx.respond('The shirt must be 585x559 pixels')

    if pants and (pants.width != 585 and pants.height != 559):
        return await ctx.respond('The pants must be 585x559 pixels')

    uid = ctx.author.id
    response = await ctx.respond(embed=PROCESSING_EMBED)

    channel = bot.get_channel(LOG_CHANNEL)
    shirt_embed = discord.Embed(
        title=f'{uid} - Shirt',
        color=discord.Color.blurple(),
        url='https://example.com'
    )

    pants_embed = discord.Embed(
        title=f'{uid} - Pants',
        color=discord.Color.blurple(),
        url='https://example.com'
    )

    embeds = []
    files = []

    if shirt:
        await shirt.save(f'temp/shirt-{uid}.png')
        shirt_embed.set_image(url=f'attachment://shirt-{uid}.png')
        embeds.append(shirt_embed)
        files.append(discord.File(f'temp/shirt-{uid}.png'))
    if pants:
        await pants.save(f'temp/pants-{uid}.png')
        pants_embed.set_image(url=f'attachment://pants-{uid}.png')
        embeds.append(pants_embed)
        files.append(discord.File(f'temp/pants-{uid}.png'))

    await channel.send(ctx.author.mention, embeds=embeds, files=files)

    shirt_color = pants_color = None

    with Image.open('assets/template.jpg') as template:
        if shirt:
            with Image.open(f'temp/shirt-{uid}.png') as shirt:
                shirt_color = place_shirt(template, shirt)

        if pants:
            with Image.open(f'temp/pants-{uid}.png') as pants:
                pants_color = place_pants(template, pants)

        template.save(f'temp/showcase-{uid}.png')

    color_alpha: tuple[int, int, int, int] = shirt_color if shirt_color else pants_color  # pyright: ignore
    color = color_alpha[:3]

    response_embed = discord.Embed(
        title=f'{ctx.author.name} showcase',
        color=discord.Color.from_rgb(*color)  # pyright: ignore
    )
    response_embed.set_image(url=f'attachment://showcase-{uid}.png')

    await response.edit(embed=response_embed, file=discord.File(f'temp/showcase-{uid}.png'))

    if shirt:
        os.remove(f'temp/shirt-{uid}.png')

    if pants:
        os.remove(f'temp/pants-{uid}.png')

    os.remove(f'temp/showcase-{uid}.png')


@bot.slash_command(name='robloxkit')
@commands.has_role(1299690637360369694)
async def robloxkit(ctx, url: discord.Option(discord.SlashCommandOptionType.string, 'The URL to the Roblox asset')):  # pyright: ignore
    await ctx.defer()

    searched = re.search(r'catalog/(\d+)', url)
    if not searched:
        return await ctx.respond('Invalid URL provided', ephemeral=True)

    asset_id = searched.group(1)
    xml = requests.get(f'https://assetdelivery.roblox.com/v1/asset?id={asset_id}').text

    if 'Asset not found' in xml:
        return await ctx.respond('Asset not found', ephemeral=True)

    root = ET.fromstring(xml)
    asset_url = root.find(".//Content")

    if asset_url is None:
        return await ctx.respond('No asset found', ephemeral=True)

    iterator = asset_url.itertext()
    _ = next(iterator)
    url = next(iterator)

    final_id = url.split('=')[-1]
    final_url = f'https://assetdelivery.roblox.com/v1/asset?id={final_id}'

    shirt = discord.File(BytesIO(requests.get(final_url).content), filename=f'{final_id}.png')

    other_data = requests.get(f"https://catalog.roblox.com/v1/catalog/items/{asset_id}/details?itemType=asset").json()
    
    name = other_data['name']
    creator = other_data['creatorName']
    sellerID = other_data['expectedSellerId']
    price = other_data['price']
    assetType = other_data['assetType']

    asset_type_text = 'Shirt' if assetType == 11 else ('Pants' if assetType == 12 else 'Unknown')

    embed = discord.Embed(
        title=name,
        description=f'[{name}]({url}) by [{creator}](https://www.roblox.com/users/{sellerID}/profile)',
        color=discord.Color.blurple()
    )

    embed.add_field(name='Price', value=f'{price} robux')
    embed.add_field(name='Asset Type', value=f'{asset_type_text} ({assetType})')

    embed.set_image(url=f'attachment://{final_id}.png')

    await ctx.respond(embed=embed, files=[shirt])


if __name__ == '__main__':
    bot.run(BOT_TOKEN)
